from enum import Enum
from vint.ast.plugin.abstract_ast_plugin import AbstractASTPlugin
from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType
from vint.ast.plugin.builtin_identifiers import BuiltinIdentifierMap


class DeclarationScope(Enum):
    GLOBAL = 1
    BUFFER_LOCAL = 2
    WINDOW_LOCAL = 3
    TAB_LOCAL = 4
    SCRIPT_LOCAL = 5
    FUNCTION_LOCAL = 6
    PARAMETER = 7
    BUILTIN = 8


class ScopeType(Enum):
    TOPLEVEL = 1
    FUNCTION = 2


class ScopePlugin(AbstractASTPlugin):
    SCOPE_TREE_KEY = 'vint_scope_tree'
    SCOPE_KEY = 'vint_scope'
    DEFINITION_IDENTIFIER_FLAG_KEY = 'VINT:is_definition_identifier'
    BUILTIN_IDENTIFIER_FLAG_KEY = 'VINT:is_builtin_identifier'

    prefix_to_declaration_scope_map = {
        'g:': DeclarationScope.GLOBAL,
        'b:': DeclarationScope.BUFFER_LOCAL,
        'w:': DeclarationScope.WINDOW_LOCAL,
        't:': DeclarationScope.TAB_LOCAL,
        's:': DeclarationScope.SCRIPT_LOCAL,
        'l:': DeclarationScope.FUNCTION_LOCAL,
        'a:': DeclarationScope.PARAMETER,
        'v:': DeclarationScope.BUILTIN,
    }


    class IdentifierNormalizationError(Exception):
        pass


    def __init__(self):
        self.node_type_to_on_enter_handler_map = {
            NodeType.TOPLEVEL: self._handle_enter_toplevel,
            NodeType.FUNCTION: self._handle_enter_function,
            NodeType.IDENTIFIER: self._handle_enter_identifier,
            NodeType.LET: self._handle_enter_destructuring_assignment_node,
            NodeType.FOR: self._handle_enter_destructuring_assignment_node,
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

        ast[ScopePlugin.SCOPE_TREE_KEY] = self.root_scope


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
        func_name_identifier = node['left']
        func_name = ScopePlugin.get_normalized_identifier(func_name_identifier)

        self._mark_difinition_identifier(func_name_identifier)
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

            self._mark_difinition_identifier(param)
            self._handle_new_variable('a:' + param_name)


    def _mark_difinition_identifier(self, identifier):
        """ Mark the identifier as definition.

        For example:

            " IDENTIFIER1 is definition.
            functrion IDENTIFIER1():
            endfunction

            " IDENTIFIER2 is not definition
            call IDENTIFIER2()
        """
        identifier[ScopePlugin.DEFINITION_IDENTIFIER_FLAG_KEY] = True


    def _handle_enter_destructuring_assignment_node(self, node):
        # See:
        #   :help :for
        #   :help :let
        is_destructuring_assignment = len(node['list']) > 0

        if is_destructuring_assignment:
            self._handle_enter_node_have_list(node)
        else:
            self._handle_enter_node_have_left_identifier(node)


    def _handle_enter_node_have_list(self, node):
        list_nodes = node['list']

        for elem_node in list_nodes:
            identifier_name = ScopePlugin.get_normalized_identifier(elem_node)

            self._mark_difinition_identifier(elem_node)
            self._handle_new_variable(identifier_name)


    def _handle_enter_node_have_left_identifier(self, node):
        left_node = node['left']
        identifier_name = ScopePlugin.get_normalized_identifier(left_node)

        self._mark_difinition_identifier(left_node)
        self._handle_new_variable(identifier_name)


    def _handle_enter_subscript(self, node):
        self._handle_enter_node_have_left_identifier(node)


    def _handle_enter_dot(self, node):
        self._handle_enter_node_have_left_identifier(node)


    def _handle_enter_identifier(self, identifier_node):
        identifier_node[ScopePlugin.SCOPE_KEY] = self.current_scope

        # Make all idenifiers to contain DEFINITION_IDENTIFIER_FLAG.
        if ScopePlugin.DEFINITION_IDENTIFIER_FLAG_KEY not in identifier_node:
            identifier_node[ScopePlugin.DEFINITION_IDENTIFIER_FLAG_KEY] = False

        identifier = identifier_node['value']
        identifier_node[ScopePlugin.BUILTIN_IDENTIFIER_FLAG_KEY] = identifier in BuiltinIdentifierMap


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


    def _handle_new_variable(self, identifier_name):
        variables_map = self.current_scope['variables']

        variable = {
            'declaration_scope':
                ScopePlugin.detect_scope(identifier_name, self.current_scope),
            'is_declared_with_implicit_scope':
                ScopePlugin.is_declared_with_implicit_scope(identifier_name),
        }

        if identifier_name in variables_map:
            # We can declare duplicated variables, and the older variable
            # will be overwrited by newer. But we interested in searching
            # duplicated variable declaration. So variables map should
            # have an array that contains all variable declaration.
            variables_map[identifier_name].append(variable)
        else:
            variables_map[identifier_name] = [variable]


    @classmethod
    def get_normalized_identifier(cls, node):
        node_type = NodeType(node['type'])

        if node_type in {NodeType.IDENTIFIER, NodeType.ENV, NodeType.OPTION, NodeType.REG}:
            return node['value']

        if node_type is NodeType.DOT or node_type is NodeType.SUBSCRIPT:
            dict_name = node['left']['value']
            key_name = ScopePlugin.get_normalized_identifier(node['right'])
            return '{dict_name}["{key_name}"]'.format(dict_name=dict_name,
                                                      key_name=key_name)
        if node_type is NodeType.STRING:
            return node['value'].strip('"\'')

        raise ScopePlugin.IdentifierNormalizationError()


    @classmethod
    def is_declared_with_implicit_scope(cls, identifier_name):
        # No declaration scope means implicit declaration.
        return ScopePlugin.detect_explicit_scope(identifier_name) is None


    @classmethod
    def detect_scope(cls, identifier_name, scope):
        if ScopePlugin.is_declared_with_implicit_scope(identifier_name):
            return ScopePlugin.detect_implicit_scope(identifier_name, scope)
        else:
            return ScopePlugin.detect_explicit_scope(identifier_name)


    @classmethod
    def detect_explicit_scope(cls, identifier_name):
        """ Returns a DeclarationScope by the specified identifier name.
        Return None when the variable have no scope-prefix.
        """

        # See:
        #   :help let-&
        #   :help let-$
        #   :help let-@
        first_char = identifier_name[0]
        if first_char in '&$@':
            return DeclarationScope.GLOBAL

        # See:
        #   :help E738
        prefix = identifier_name[0:2]
        if prefix in ScopePlugin.prefix_to_declaration_scope_map:
            return ScopePlugin.prefix_to_declaration_scope_map[prefix]

        # It is GLOBAL or FUNCTION_LOCAL, but we cannot determine without the
        # parent scope.
        return None


    @classmethod
    def detect_implicit_scope(cls, identifier_name, scope):
        is_toplevel_context = scope['type'] is ScopeType.TOPLEVEL

        # See :help internal-variables
        # > In a function: local to a function; otherwise: global
        if is_toplevel_context:
            return DeclarationScope.GLOBAL
        else:
            return DeclarationScope.FUNCTION_LOCAL
