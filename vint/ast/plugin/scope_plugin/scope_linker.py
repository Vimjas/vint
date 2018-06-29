from typing import Dict, Any, Union, Optional
from vint.ast.traversing import traverse, SKIP_CHILDREN
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.identifier_syntax import remove_optional_scope_prefix
from vint.ast.plugin.scope_plugin.scope import Scope, VariableDeclaration
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeVisibility,
    ExplicityOfScopeVisibility,
    detect_possible_scope_visibility,
    is_analyzable_identifier,
    is_analyzable_declarative_identifier,
    is_builtin_variable,
    is_function_identifier,
)
from vint.ast.plugin.scope_plugin.identifier_classifier import IdentifierClassifier


DeclarativeNodeTypes = {
    NodeType.FUNCTION: True,
    NodeType.LET: True,
    NodeType.FOR: True,
}


FunctionNameNodesDeclaringVariableSelf = {
    NodeType.DOT: True,
    NodeType.SUBSCRIPT: True,
}


SymbolTableVariableNames = {
    ScopeVisibility.GLOBAL_LIKE: ['g:', 'b:', 'w:', 't:', 'v:'],
    ScopeVisibility.SCRIPT_LOCAL: ['s:'],
    ScopeVisibility.FUNCTION_LOCAL: ['l:', 'a:'],
    ScopeVisibility.LAMBDA: [],
}


class ScopeLinker(object):
    """ A class for scope linkers.
    The class link identifiers in the given AST node and the scopes where the
    identifier will be declared or referenced.
    """

    class ScopeTreeBuilder(object):
        """ A class for event-driven builders to build a scope tree.
        The class interest to scope-level events rather than AST-level events.
        """

        def __init__(self):
            self.link_registry = ScopeLinker.ScopeLinkRegistry()

            global_scope = Scope(ScopeVisibility.GLOBAL_LIKE)
            self._scope_stack = [global_scope]
            self._add_symbol_table_variables(global_scope)


        def enter_new_scope(self, scope_visibility): # type: (ScopeVisibility) -> None
            current_scope = self.get_current_scope()
            new_scope = Scope(scope_visibility)
            self._add_symbol_table_variables(new_scope)

            # Build a lexical scope chain
            current_scope.child_scopes.append(new_scope)
            self._scope_stack.append(new_scope)


        def leave_current_scope(self): # type: () -> None
            self._scope_stack.pop()


        def get_global_scope(self): # type: () -> Scope
            return self._scope_stack[0]


        def get_script_local_scope(self): # type: () -> Scope
            return self._scope_stack[1]


        def get_current_scope(self): # type: () -> Scope
            return self._scope_stack[-1]


        def handle_new_parameter_found(self, id_node, is_lambda_argument): # type: (Dict[str, Any], bool) -> None
            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, id_node, is_lambda_argument)


        def handle_new_range_parameters_found(self): # type: () -> None
            # We can access "a:firstline" and "a:lastline" if the function is
            # declared with an attribute "range". See :func-range
            firstline_node = _create_virtual_identifier_node('firstline')
            lastline_node = _create_virtual_identifier_node('lastline')

            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, firstline_node, is_explicit_lambda_argument=False)
            self._add_parameter(current_scope, lastline_node, is_explicit_lambda_argument=False)


        def handle_new_dict_parameter_found(self): # type: () -> None
            # We can access "l:self" is declared with an attribute "dict".
            # See :help self
            current_scope = self.get_current_scope()
            self._add_self_variable(current_scope)


        def handle_new_parameters_list_and_length_found(self): # type: () -> None
            # We can always access a:0 and a:000
            # See :help internal-variables
            param_length_node = _create_virtual_identifier_node('0')
            param_list_node = _create_virtual_identifier_node('000')

            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, param_length_node, is_explicit_lambda_argument=False)
            self._add_parameter(current_scope, param_list_node, is_explicit_lambda_argument=False)


        def handle_new_index_parameters_found(self, params_number): # type: (int) -> None
            current_scope = self.get_current_scope()

            # Max parameters number is 20. See :help E740
            for variadic_index in range(20 - params_number):
                # Variadic parameters named 1-based index.
                variadic_param = _create_virtual_identifier_node(str(variadic_index + 1))
                self._add_parameter(current_scope, variadic_param, is_explicit_lambda_argument=False)


        def handle_new_variable_found(self, id_node): # type: (Dict[str, Any]) -> None
            current_scope = self.get_current_scope()
            scope_visibility_hint = detect_possible_scope_visibility(id_node, current_scope)

            if scope_visibility_hint.scope_visibility is ScopeVisibility.UNANALYZABLE \
                    or scope_visibility_hint.scope_visibility is ScopeVisibility.INVALID:
                # We can not do anything
                return

            is_function = is_function_identifier(id_node)

            if is_builtin_variable(id_node):
                self._add_builtin_variable(id_node,
                                           is_function=is_function,
                                           explicity=scope_visibility_hint.explicity)
                return

            objective_scope = self._get_objective_scope(id_node)
            self._add_variable(objective_scope,
                               id_node,
                               is_function,
                               scope_visibility_hint.explicity)


        def _get_objective_scope(self, node): # type: (Dict[str, Any]) -> Scope

            current_scope = self.get_current_scope()
            scope_visibility_hint = detect_possible_scope_visibility(
                node, current_scope)
            scope_visibility = scope_visibility_hint.scope_visibility

            if scope_visibility is ScopeVisibility.GLOBAL_LIKE:
                return self.get_global_scope()

            if scope_visibility is ScopeVisibility.SCRIPT_LOCAL:
                return self.get_script_local_scope()

            # It is FUNCTION_LOCAL or LAMBDA scope
            return current_scope


        def handle_referencing_identifier_found(self, node): # type: (Dict[str, Any]) -> None
            current_scope = self.get_current_scope()

            self.link_registry.link_identifier_to_context_scope(node, current_scope)


        def _add_parameter(self, objective_scope, id_node, is_explicit_lambda_argument):
            # type: (Scope, Dict[str, Any], bool) -> None
            if is_explicit_lambda_argument:
                # Explicit lambda arguments can not have any explicit scope prefix.
                variable_name = id_node['value']
                explicity = ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED
            else:
                variable_name = 'a:' + id_node['value']
                explicity = ExplicityOfScopeVisibility.EXPLICIT

            self._register_variable(
                objective_scope,
                variable_name,
                id_node,
                explicity=explicity,
                is_function=False,
                is_builtin=False,
                is_explicit_lambda_argument=is_explicit_lambda_argument
            )


        def _add_self_variable(self, objective_scope): # type: (Scope) -> None
            variable_name = remove_optional_scope_prefix('l:self')
            virtual_node = _create_virtual_identifier_node(variable_name)

            self._register_variable(
                objective_scope,
                variable_name,
                virtual_node,
                explicity=ExplicityOfScopeVisibility.EXPLICIT,
                is_function=False,
                is_builtin=False,
                is_explicit_lambda_argument=False
            )


        def _add_variable(self, objective_scope, id_node, is_function, explicity):
            # type: (Scope, Dict[str, Any], bool, ExplicityOfScopeVisibility) -> None
            variable_name = remove_optional_scope_prefix(id_node['value'])

            self._register_variable(
                objective_scope,
                variable_name,
                id_node,
                explicity,
                is_function,
                is_builtin=False,
                is_explicit_lambda_argument=False
            )


        def _add_builtin_variable(self, id_node, explicity, is_function):
            # type: (Dict[str, Any], ExplicityOfScopeVisibility, bool) -> None
            variable_name = remove_optional_scope_prefix(id_node['value'])

            self._register_variable(
                self.get_global_scope(),
                variable_name,
                id_node,
                explicity,
                is_function,
                is_builtin=True,
                is_explicit_lambda_argument=False
            )


        def _add_symbol_table_variables(self, objective_scope): # type: (Scope) -> None
            # We can always access any symbol tables such as: "g:", "s:", "l:".
            # See :help internal-variables
            scope_visibility = objective_scope.scope_visibility
            symbol_table_variable_names = SymbolTableVariableNames[scope_visibility]

            for symbol_table_variable_name in symbol_table_variable_names:
                virtual_node = _create_virtual_identifier_node(symbol_table_variable_name)

                self._register_variable(
                    objective_scope,
                    symbol_table_variable_name,
                    virtual_node,
                    # NOTE: Symbol table always have scope prefix.
                    explicity=ExplicityOfScopeVisibility.EXPLICIT,
                    is_builtin=False,
                    is_function=False,
                    is_explicit_lambda_argument=False
                )


        def _register_variable(self, objective_scope, variable_name, node, explicity, is_function, is_builtin, is_explicit_lambda_argument):
            # type: (Scope, str, Dict[str, Any], ExplicityOfScopeVisibility, bool, bool, bool) -> None
            variable = VariableDeclaration(
                explicity,
                is_builtin,
                is_explicit_lambda_argument
            )

            if is_function:
                objective_variable_list = objective_scope.functions
            else:
                objective_variable_list = objective_scope.variables

            same_name_variables = objective_variable_list.setdefault(variable_name, [])
            same_name_variables.append(variable)

            self.link_registry.link_variable_to_declarative_identifier(variable, node)

            current_scope = self.get_current_scope()
            self.link_registry.link_identifier_to_context_scope(node, current_scope)



    class ScopeLinkRegistry(object):
        """ A class for registry services for links between scopes and
        identifiers.
        """

        def __init__(self):
            self._vars_to_declarative_ids_map = {}  # type: Dict[int, Dict[str, Any]]
            self._ids_to_scopes_map = {}  # type: Dict[int, Scope]


        def link_variable_to_declarative_identifier(self, variable, declaring_id_node):
            # type: (VariableDeclaration, Dict[str, Any]) -> None
            self._vars_to_declarative_ids_map[id(variable)] = declaring_id_node


        def get_declarative_identifier_by_variable(self, variable): # type: (VariableDeclaration) -> Dict[str, Any]
            variable_id = id(variable)
            return self._vars_to_declarative_ids_map.get(variable_id)


        def link_identifier_to_context_scope(self, decl_or_ref_id_node, scope): # type: (Dict[str, Any], Scope) -> None
            """ Link declarative identifier node or reference identifier node to
            the lexical context scope that the identifier is presented at. """
            node_id = id(decl_or_ref_id_node)
            self._ids_to_scopes_map[node_id] = scope


        def get_context_scope_by_identifier(self, decl_or_ref_id_node): # type: (Dict[str, Any]) -> Scope
            """ Return the lexical context scope that the identifier is presented at by
            a declarative identifier node or a reference identifier node """
            node_id = id(decl_or_ref_id_node)
            return self._ids_to_scopes_map.get(node_id)


    def __init__(self):
        self.scope_tree = None  # type: Union[Scope, None]
        self.link_registry = None  # type: ScopeLinker.ScopeLinkRegistry

        self._scope_tree_builder = ScopeLinker.ScopeTreeBuilder()


    def process(self, ast): # type: (Dict[str, Any]) -> None
        """ Build a scope tree and links between scopes and identifiers by the
        specified ast. You can access the built scope tree and the built links
        by .scope_tree and .link_registry.
        """
        id_classifier = IdentifierClassifier()
        attached_ast = id_classifier.attach_identifier_attributes(ast)

        # We are already in script local scope.
        self._scope_tree_builder.enter_new_scope(ScopeVisibility.SCRIPT_LOCAL)

        traverse(attached_ast,
                 on_enter=self._enter_handler,
                 on_leave=self._leave_handler)

        self.scope_tree = self._scope_tree_builder.get_global_scope()
        self.link_registry = self._scope_tree_builder.link_registry


    def _find_variable_like_nodes(self, node): # type: (Dict[str, Any]) -> None
        if not is_analyzable_identifier(node):
            return

        if is_analyzable_declarative_identifier(node):
            self._scope_tree_builder.handle_new_variable_found(node)
            return

        self._scope_tree_builder.handle_referencing_identifier_found(node)


    def _enter_handler(self, node): # type: (Dict[str, Any]) -> None
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            return self._handle_function_node(node)
        elif node_type is NodeType.LAMBDA:
            return self._handle_lambda_node(node)

        self._find_variable_like_nodes(node)


    def _handle_function_node(self, func_node): # type: (Dict[str, Any]) -> None
        # We should interrupt traversing, because a node of the function
        # name should be added to the parent scope before the current
        # scope switched to a new scope of the function.
        # We approach to it by the following 5 steps.
        #   1. Add the function to the current scope
        #   2. Create a new scope of the function
        #   3. The current scope point to the new scope
        #   4. Add parameters to the new scope
        #   5. Add variables in the function body to the new scope

        # 1. Add the function to the current scope
        func_name_node = func_node['left']
        traverse(func_name_node, on_enter=self._find_variable_like_nodes)

        # 2. Create a new scope of the function
        # 3. The current scope point to the new scope
        self._scope_tree_builder.enter_new_scope(ScopeVisibility.FUNCTION_LOCAL)

        has_variadic = False

        # 4. Add parameters to the new scope
        param_nodes = func_node['rlist']
        for param_node in param_nodes:
            if param_node['value'] == '...':
                has_variadic = True
            else:
                # the param_node type is always NodeType.IDENTIFIER
                self._scope_tree_builder.handle_new_parameter_found(param_node, is_lambda_argument=False)

        # We can always access a:0, a:000
        self._scope_tree_builder.handle_new_parameters_list_and_length_found()

        # In a variadic function, we can access a:1 ... a:n
        # (n = 20 - explicit parameters length). See :help a:0
        if has_variadic:
            # -1 means ignore '...'
            self._scope_tree_builder.handle_new_index_parameters_found(len(param_nodes) - 1)

        # We can access "a:firstline" and "a:lastline" if the function is
        # declared with an attribute "range". See :func-range
        attr = func_node['attr']
        is_declared_with_range = attr['range'] is not 0
        if is_declared_with_range:
            self._scope_tree_builder.handle_new_range_parameters_found()

        # We can access "l:self" is declared with an attribute "dict" or
        # the function is a member of a dict. See :help self
        is_declared_with_dict = attr['dict'] is not 0 \
            or NodeType(func_name_node['type']) in FunctionNameNodesDeclaringVariableSelf
        if is_declared_with_dict:
            self._scope_tree_builder.handle_new_dict_parameter_found()

        # 5. Add variables in the function body to the new scope
        func_body_nodes = func_node['body']
        for func_body_node in func_body_nodes:
            traverse(func_body_node,
                     on_enter=self._enter_handler,
                     on_leave=self._leave_handler)

        # Skip child nodes traversing
        return SKIP_CHILDREN


    def _handle_lambda_node(self, lambda_node): # type: (Dict[str, Any]) -> Optional[str]
        # This method do the following 4 steps:
        #   1. Create a new scope of the lambda
        #   2. The current scope point to the new scope
        #   3. Add parameters to the new scope
        #   4. Add variables in the function body to the new scope

        # 1. Create a new scope of the function
        # 2. The current scope point to the new scope
        self._scope_tree_builder.enter_new_scope(ScopeVisibility.LAMBDA)

        # 3. Add parameters to the new scope
        has_variadic_symbol = False
        param_nodes = lambda_node['rlist']
        for param_node in param_nodes:
            if param_node['value'] == '...':
                has_variadic_symbol = True
            else:
                # the param_node type is always NodeType.IDENTIFIER
                self._scope_tree_builder.handle_new_parameter_found(param_node, is_lambda_argument=True)

        # We can access a:0 and a:000 when the number of arguments is less than actual parameters.
        self._scope_tree_builder.handle_new_parameters_list_and_length_found()

        # In the context of lambda, we can access a:1 ... a:n when the number of arguments is less than actual parameters.
        # XXX: We can not know what a:N we can access by static analysis, so we assume it is 20.
        if has_variadic_symbol:
            lambda_args_len = len(param_nodes) - 1
        else:
            lambda_args_len = len(param_nodes)

        self._scope_tree_builder.handle_new_index_parameters_found(lambda_args_len)

        # 4. Add variables in the function body to the new scope
        traverse(lambda_node['left'],
                 on_enter=self._enter_handler,
                 on_leave=self._leave_handler)

        # Skip child nodes traversing
        return SKIP_CHILDREN


    def _leave_handler(self, node): # type: (Dict[str, Any]) -> None
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            self._scope_tree_builder.leave_current_scope()

        elif node_type is NodeType.LAMBDA:
            self._scope_tree_builder.leave_current_scope()


def _create_virtual_identifier_node(id_value): # type: (str) -> Dict[str, Any]
    """ Returns a virtual identifier.
    Virtual identifier is a virtual node for implicitly declared
    variables such as: a:0, a:000, a:firstline.
    """
    return {
        'type': NodeType.IDENTIFIER.value,
        'value': id_value,
        'is_virtual': True,
    }
