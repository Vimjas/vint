from vint.ast.traversing import traverse, SKIP_CHILDREN
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeVisibility,
    detect_scope_visibility,
    is_analyzable_identifier,
    is_analyzable_declarative_identifier,
    is_builtin_variable,
    normalize_variable_name,
)
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IdentifierClassifier,
    is_function_identifier,
)


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

            global_scope = self._create_scope(ScopeVisibility.GLOBAL_LIKE)
            self._scope_stack = [global_scope]
            self._add_symbol_table_variables(global_scope)


        def enter_new_scope(self, scope_visibility):
            current_scope = self.get_current_scope()
            new_scope = self._create_scope(scope_visibility)
            self._add_symbol_table_variables(new_scope)

            # Build a lexical scope chain
            current_scope['child_scopes'].append(new_scope)
            self._scope_stack.append(new_scope)


        def leave_current_scope(self):
            self._scope_stack.pop()


        def get_global_scope(self):
            return self._scope_stack[0]


        def get_script_local_scope(self):
            return self._scope_stack[1]


        def get_current_scope(self):
            return self._scope_stack[-1]


        def handle_new_parameter_found(self, id_node):
            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, id_node)


        def handle_new_range_parameters_found(self):
            # We can access "a:firstline" and "a:lastline" if the function is
            # declared with an attribute "range". See :func-range
            firstline_node = self._create_virtual_identifier('firstline')
            lastline_node = self._create_virtual_identifier('lastline')

            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, firstline_node)
            self._add_parameter(current_scope, lastline_node)


        def handle_new_dict_parameter_found(self):
            # We can access "l:self" is declared with an attribute "dict".
            # See :help self
            current_scope = self.get_current_scope()
            self._add_self_variable(current_scope)


        def handle_new_parameters_list_and_length_found(self):
            # We can always access a:0 and a:000
            # See :help internal-variables
            param_length_node = self._create_virtual_identifier('0')
            param_list_node = self._create_virtual_identifier('000')

            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, param_length_node)
            self._add_parameter(current_scope, param_list_node)


        def handle_new_index_parameters_found(self, params_number):
            current_scope = self.get_current_scope()

            # Max parameters number is 20. See :help E740
            for variadic_index in range(20 - params_number):
                # Variadic parameters named 1-based index.
                variadic_param = self._create_virtual_identifier(str(variadic_index + 1))
                self._add_parameter(current_scope, variadic_param)


        def handle_new_variable_found(self, node):
            current_scope = self.get_current_scope()
            scope_visibility_hint = detect_scope_visibility(
                node, current_scope)

            if scope_visibility_hint is None:
                # We cannot do anything
                return

            is_implicit = scope_visibility_hint['is_implicit']
            is_function = is_function_identifier(node)

            if is_builtin_variable(node):
                self._add_builtin_variable(node,
                                           is_function=is_function,
                                           is_implicit=is_implicit)
                return

            objective_scope = self._get_objective_scope(node)
            self._add_variable(objective_scope,
                               node,
                               is_function=is_function,
                               is_implicit=is_implicit)


        def _get_objective_scope(self, node):
            current_scope = self.get_current_scope()
            scope_visibility_hint = detect_scope_visibility(
                node, current_scope)
            scope_visibility = scope_visibility_hint['scope_visibility']

            if scope_visibility is ScopeVisibility.GLOBAL_LIKE:
                return self.get_global_scope()

            if scope_visibility is ScopeVisibility.SCRIPT_LOCAL:
                return self.get_script_local_scope()

            # It is FUNCTION_LOCAL scope
            return current_scope


        def handle_referencing_identifier_found(self, node):
            current_scope = self.get_current_scope()

            self.link_registry.link_identifier_to_context_scope(node, current_scope)


        def _add_parameter(self, objective_scope, node):
            variable_name = 'a:' + node['value']
            self._register_variable(objective_scope, variable_name, node)


        def _add_self_variable(self, objective_scope):
            variable_name = 'l:self'
            virtual_node = self._create_virtual_identifier(variable_name)
            self._register_variable(objective_scope, variable_name, virtual_node)


        def _add_variable(self, objective_scope, node, is_implicit=False, is_function=False):
            current_scope = self.get_current_scope()
            variable_name = normalize_variable_name(node, current_scope)

            self._register_variable(objective_scope,
                                    variable_name,
                                    node,
                                    is_function=is_function,
                                    is_implicit=is_implicit)


        def _add_builtin_variable(self, node, is_implicit=False, is_function=False):
            current_scope = self.get_current_scope()
            variable_name = normalize_variable_name(node, current_scope)

            self._register_variable(self.get_global_scope(),
                                    variable_name,
                                    node,
                                    is_implicit=is_implicit,
                                    is_function=is_function,
                                    is_builtin=True)
            return


        def _add_symbol_table_variables(self, objective_scope):
            # We can always access any symbol tables such as: "g:", "s:", "l:".
            # See :help internal-variables
            scope_visibility = objective_scope['scope_visibility']
            symbol_table_variable_names = SymbolTableVariableNames[scope_visibility]

            for symbol_table_variable_name in symbol_table_variable_names:
                virtual_node = self._create_virtual_identifier(symbol_table_variable_name)

                self._register_variable(objective_scope,
                                        symbol_table_variable_name,
                                        virtual_node)


        def _register_variable(self, objective_scope, variable_name, node,
                               is_implicit=False, is_builtin=False, is_function=False):
            variable = self._create_variable(is_implicit=is_implicit,
                                             is_builtin=is_builtin)

            objective_variable_list = objective_scope['functions' if is_function
                                                      else 'variables']

            same_name_variables = objective_variable_list.setdefault(variable_name, [])
            same_name_variables.append(variable)

            self.link_registry.link_variable_to_declarative_identifier(variable, node)

            current_scope = self.get_current_scope()
            self.link_registry.link_identifier_to_context_scope(node, current_scope)


        def _create_variable(self, is_implicit=False, is_builtin=False):
            return {
                'is_implicit': is_implicit,
                'is_builtin': is_builtin,
            }


        def _create_scope(self, scope_visibility):
            scope = {
                'scope_visibility': scope_visibility,
                'functions': {},
                'variables': {},
                'child_scopes': [],
            }

            return scope


        def _create_virtual_identifier(self, id_value):
            """ Returns a virtual identifier.
            Virtual identifier is a virtual node for implicitly declarated
            variables such as: a:0, a:000, a:firstline.
            """
            return {
                'type': NodeType.IDENTIFIER.value,
                'value': id_value,
                'is_virtual': True,
            }



    class ScopeLinkRegistry(object):
        """ A class for registry services for links between scopes and
        identifiers.
        """

        def __init__(self):
            self._vars_to_declarative_ids_map = {}
            self._ids_to_scopes_map = {}


        def link_variable_to_declarative_identifier(self, variable, declaring_id_node):
            variable_id = id(variable)
            self._vars_to_declarative_ids_map[variable_id] = declaring_id_node


        def link_identifier_to_context_scope(self, id_node, scope):
            node_id = id(id_node)
            self._ids_to_scopes_map[node_id] = scope


        def get_declarative_identifier_by_variable(self, variable):
            variable_id = id(variable)
            return self._vars_to_declarative_ids_map.get(variable_id)


        def get_context_scope_by_identifier(self, identifier):
            node_id = id(identifier)
            return self._ids_to_scopes_map.get(node_id)


    def __init__(self):
        self.scope_tree = None
        self.link_registry = None


    def process(self, ast):
        """ Build a scope tree and links between scopes and identifiers by the
        specified ast. You can access the built scope tree and the built links
        by .scope_tree and .link_registry.
        """
        id_classifier = IdentifierClassifier()
        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self._scope_tree_builder = ScopeLinker.ScopeTreeBuilder()

        # We are already in script local scope.
        self._scope_tree_builder.enter_new_scope(ScopeVisibility.SCRIPT_LOCAL)

        traverse(attached_ast,
                 on_enter=self._enter_handler,
                 on_leave=self._leave_handler)

        self.scope_tree = self._scope_tree_builder.get_global_scope()
        self.link_registry = self._scope_tree_builder.link_registry


    def _find_variable_like_nodes(self, node):
        if not is_analyzable_identifier(node):
            return

        if is_analyzable_declarative_identifier(node):
            self._scope_tree_builder.handle_new_variable_found(node)
            return

        self._scope_tree_builder.handle_referencing_identifier_found(node)


    def _enter_handler(self, node):
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            return self._handle_function_node(node)

        self._find_variable_like_nodes(node)


    def _handle_function_node(self, func_node):
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
                self._scope_tree_builder.handle_new_parameter_found(param_node)

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


    def _leave_handler(self, node):
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            self._scope_tree_builder.leave_current_scope()
