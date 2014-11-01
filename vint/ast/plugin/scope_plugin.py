from enum import Enum
from vint.ast.plugin.abstract_ast_plugin import AbstractASTPlugin
from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType


class DeclarationScope(Enum):
    GLOBAL = 1
    BUFFER_LOCAL = 2
    WINDOW_LOCAL = 3
    TAB_LOCAL = 4
    SCRIPT_LOCAL = 5
    FUNCTION_LOCAL = 6
    PARAMETER = 7


class ScopeType(Enum):
    TOPLEVEL = 1
    FUNCTION = 2


class ScopePlugin(AbstractASTPlugin):
    prefix_to_declaration_scope_map = {
        'g:': DeclarationScope.GLOBAL,
        'b:': DeclarationScope.BUFFER_LOCAL,
        'w:': DeclarationScope.WINDOW_LOCAL,
        't:': DeclarationScope.TAB_LOCAL,
        's:': DeclarationScope.SCRIPT_LOCAL,
        'l:': DeclarationScope.FUNCTION_LOCAL,
        'a:': DeclarationScope.PARAMETER,
    }


    def __init__(self):
        self.node_type_to_on_enter_handler_map = {
            NodeType.TOPLEVEL: self._handle_enter_toplevel,
            NodeType.FUNCTION: self._handle_enter_function,
            NodeType.LET: self._handle_enter_let,
            NodeType.FOR: self._handle_enter_for,
        }

        self.node_type_to_on_leave_handler_map = {
            NodeType.FUNCTION: self._handle_leave_function,
        }


    def process(self, ast):
        self.current_scope = []
        self.root_scope = None

        traverse(ast,
                 on_enter=self._handle_enter,
                 on_leave=self._handle_leave)

        ast.vint_scope_tree = self.root_scope


    def _handle_enter(self, node):
        node_type = NodeType(node['type'])

        if node_type not in self.node_type_to_on_enter_handler_map:
            return

        enter_handler = self.node_type_to_on_enter_handler_map[node_type]
        enter_handler(node)


    def _handle_enter_toplevel(self, node):
        self.root_scope = self.current_scope = {
            'type': ScopeType.TOPLEVEL,
            'variables': {},
            'parent_scope': None,
            'child_scopes': {},
        }


    def _handle_enter_function(self, node):
        func_name = node['left']['value']

        self._handle_new_variable(func_name)
        self._handle_new_scope(func_name)

        is_declared_with_range = node['attr']['range'] is not 0
        if is_declared_with_range:
            # "a:firstline" and "a:lastline" are declared automatically when
            # the function has a "range" attribute. See :func-range
            self._handle_new_variable('a:firstline')
            self._handle_new_variable('a:lastline')

        params = node['rlist']
        for param in params:
            param_name = param['value']

            if param_name == '...':
                # We may get a variable-length parameters token '...' because
                # viml-vimparser can not recognize variable-length parameters.
                # So we should ignore '...' token.
                continue

            self._handle_new_variable('a:' + param_name)


    def _handle_enter_let(self, node):
        var_name = node['left']['value']
        self._handle_new_variable(var_name)


    def _handle_enter_for(self, node):
        loop_var_name = node['left']['value']
        self._handle_new_variable(loop_var_name)


    def _handle_leave(self, node):
        node_type = NodeType(node['type'])

        if node_type not in self.node_type_to_on_leave_handler_map:
            return

        leave_handler = self.node_type_to_on_leave_handler_map[node_type]
        leave_handler(node)


    def _handle_leave_function(self, node):
        self.current_scope = self.current_scope['parent_scope']


    def _handle_new_scope(self, scope_name):
        parent_scope = self.current_scope
        sibling_scopes = parent_scope['child_scopes']

        new_scope = {
            'type': ScopeType.FUNCTION,
            'variables': {},
            'parent_scope': parent_scope,
            'child_scopes': {},
        }

        if scope_name in sibling_scopes:
            # We can declare a function with duplicated name, and the older
            # function will be overwrited by the newer. But we interested in
            # searching duplicated function declaration. So scope map should
            # have an array that contains all scopese.
            sibling_scopes[scope_name].append(new_scope)
        else:
            sibling_scopes[scope_name] = [new_scope]

        self.current_scope = new_scope


    def _handle_new_variable(self, name):
        variables_map = self.current_scope['variables']

        declaration_scope = self.detect_variable_declaration_scope(name)

        # No declaration scope means implicit declaration.
        is_declared_with_implicit_scope = declaration_scope is None

        if is_declared_with_implicit_scope:
            is_toplevel_context = self.current_scope['type'] is ScopeType.TOPLEVEL

            # See :help internal-variables
            # > In a function: local to a function; otherwise: global
            declaration_scope = None
            if is_toplevel_context:
                declaration_scope = DeclarationScope.GLOBAL
            else:
                declaration_scope = DeclarationScope.FUNCTION_LOCAL

        var = {
            'declaration_scope': declaration_scope,
            'is_declared_with_implicit_scope': is_declared_with_implicit_scope,
        }

        if name in variables_map:
            # We can declare duplicated variables, and the older variable
            # will be overwrited by newer. But we interested in searching
            # duplicated variable declaration. So variables map should
            # have an array that contains all variable declaration.
            variables_map[name].append(var)
        else:
            variables_map[name] = [var]


    def detect_variable_declaration_scope(self, var_name):
        """ Returns a DeclarationScope by the specified variable name.
        Return None when the variable have no scope-prefix.
        """
        prefix = var_name[0:2]

        if prefix not in ScopePlugin.prefix_to_declaration_scope_map:
            return None

        return ScopePlugin.prefix_to_declaration_scope_map[prefix]
