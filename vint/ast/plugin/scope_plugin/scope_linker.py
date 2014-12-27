from vint.ast.traversing import traverse, SKIP_CHILDREN
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeDetector,
    ScopeVisibility,
)

SCOPE_TREE = 'VINT:scope_tree'
SCOPE = 'VINT:scope'


DeclarativeNodeTypes = {
    NodeType.FUNCTION: True,
    NodeType.LET: True,
    NodeType.FOR: True,
}



class ScopeLinker(object):
    """ A class for scope linker.
    The class link identifiers in the given AST node and the scopes where the
    identifier will be declared or referenced.
    """

    class ScopeTreeBuilder(object):
        """ A class for event-driven builders to build a scope tree.
        The class interest to scope-level events rather than AST-level events.
        """
        def __init__(self):
            global_scope = self._create_scope(ScopeVisibility.GLOBAL_LIKE)
            self.scope_stack = [global_scope]


        def enter_new_scope(self, scope_visibility):
            current_scope = self.get_current_scope()
            new_scope = self._create_scope(scope_visibility)

            # Build a lexical scope chain
            current_scope['child_scopes'].append(new_scope)
            self.scope_stack.append(new_scope)


        def leave_current_scope(self):
            self.scope_stack.pop()


        def get_global_scope(self):
            return self.scope_stack[0]


        def get_script_local_scope(self):
            return self.scope_stack[1]


        def get_current_scope(self):
            return self.scope_stack[-1]


        def handle_new_parameter_found(self, id_node):
            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, id_node)


        def handle_new_range_parameters_found(self):
            firstline_node = self._create_virtual_identifier('firstline')
            lastline_node = self._create_virtual_identifier('lastline')

            current_scope = self.get_current_scope()
            self._add_parameter(current_scope, firstline_node)
            self._add_parameter(current_scope, lastline_node)


        def handle_new_parameters_list_and_length_found(self):
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
            scope_visibility_hint = ScopeDetector.detect_scope_visibility(node, current_scope)

            scope_visibility = scope_visibility_hint['scope_visibility']
            is_implicit = scope_visibility_hint['is_implicit']

            if scope_visibility is ScopeVisibility.GLOBAL_LIKE:
                self._add_variable(self.get_global_scope(), node, is_implicit=is_implicit)
                return

            if scope_visibility is ScopeVisibility.SCRIPT_LOCAL:
                self._add_variable(self.get_script_local_scope(), node, is_implicit=is_implicit)
                return

            # It is FUNCTION_LOCAL scope
            self._add_variable(current_scope, node, is_implicit=is_implicit)


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


        def _add_parameter(self, objective_scope, node):
            variable_name = ScopeDetector.normalize_parameter_name(node)
            variable = self._create_variable(node)

            self._add_variable_by_name(objective_scope, variable_name, variable)


        def _add_variable(self, objective_scope, node, is_implicit=False):
            current_scope = self.get_current_scope()

            is_builtin = NodeType(node['type']) is NodeType.IDENTIFIER and \
                ScopeDetector.is_builtin_variable(node)

            if is_builtin:
                self._add_builtin_variable(node, is_implicit=is_implicit)
                return

            variable_name = ScopeDetector.normalize_variable_name(node, current_scope)
            variable = self._create_variable(node,
                                             is_implicit=is_implicit)

            self._add_variable_by_name(objective_scope, variable_name, variable)


        def _add_builtin_variable(self, node, is_implicit=False):
            current_scope = self.get_current_scope()

            variable_name = ScopeDetector.normalize_variable_name(node, current_scope)
            variable = self._create_variable(node,
                                             is_implicit=is_implicit,
                                             is_builtin=True)

            self._add_variable_by_name(self.get_global_scope(), variable_name, variable)
            return


        def _add_variable_by_name(self, objective_scope, variable_name, variable):
            same_name_variables = objective_scope['variables'].get(variable_name, [])
            same_name_variables.append(variable)

            objective_scope['variables'][variable_name] = same_name_variables


        def _create_variable(self, node, is_implicit=False, is_builtin=False):
            return {
                'node': node,
                'is_implicit': is_implicit,
                'is_builtin': is_builtin,
            }


        def _create_scope(self, scope_visibility):
            return {
                'scope_visibility': scope_visibility,
                'variables': {},
                'child_scopes': [],
            }


    def process(self, ast):
        self.scope_store = ScopeLinker.ScopeTreeBuilder()

        # We are already in script local scope.
        self.scope_store.enter_new_scope(ScopeVisibility.SCRIPT_LOCAL)

        traverse(ast,
                 on_enter=self._enter_handler,
                 on_leave=self._leave_handler)

        ast[SCOPE_TREE] = self.scope_store.get_global_scope()


    def _find_new_variable(self, node):
        if not ScopeDetector.is_analyzable_identifier(node):
            return

        node[SCOPE] = self.scope_store.get_current_scope()

        if not ScopeDetector.is_analyzable_definition_identifier(node):
            return

        self.scope_store.handle_new_variable_found(node)


    def _enter_handler(self, node):
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            return self._handle_function_node(node)

        self._find_new_variable(node)


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
        traverse(func_name_node, on_enter=self._find_new_variable)

        # 2. Create a new scope of the function
        # 3. The current scope point to the new scope
        self.scope_store.enter_new_scope(ScopeVisibility.FUNCTION_LOCAL)

        has_variadic = False

        # 4. Add parameters to the new scope
        param_nodes = func_node['rlist']
        for param_node in param_nodes:
            if param_node['value'] == '...':
                has_variadic = True
            else:
                # the param_node type is always NodeType.IDENTIFIER
                self.scope_store.handle_new_parameter_found(param_node)

        # We can always access a:0 and a:000
        self.scope_store.handle_new_parameters_list_and_length_found()

        # In a variadic function, we can access a:1 ... a:n
        # (n = 20 - explicit parameters length). See :help a:0
        if has_variadic:
            # -1 means ignore '...'
            self.scope_store.handle_new_index_parameters_found(len(param_nodes) - 1)

        # We can access "a:firstline" and "a:lastline" if the function is
        # declared with an attribute "range". See :func-range
        is_declared_with_range = func_node['attr']['range'] is not 0
        if is_declared_with_range:
            self.scope_store.handle_new_range_parameters_found()

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
            self.scope_store.leave_current_scope()
