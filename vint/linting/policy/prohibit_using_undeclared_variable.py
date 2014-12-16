import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.ast.plugin.scope_plugin import ScopePlugin, DeclarationScope
from vint.linting.policy_loader import register_policy


# @register_policy
class ProhibitUsingUndeclaredVariable(AbstractPolicy):
    identifier_tracability_map = {
        DeclarationScope.GLOBAL: False,
        DeclarationScope.WINDOW_LOCAL: False,
        DeclarationScope.BUFFER_LOCAL: False,
        DeclarationScope.TAB_LOCAL: False,
        DeclarationScope.BUILTIN: False,

        DeclarationScope.SCRIPT_LOCAL: True,
        DeclarationScope.FUNCTION_LOCAL: True,
        DeclarationScope.PARAMETER: True,
    }


    def __init__(self):
        super(ProhibitUsingUndeclaredVariable, self).__init__()
        self.description = 'Variable is not declared'
        self.reference = ':help E738'
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.IDENTIFIER]

    def is_valid(self, node, lint_context):
        """ Whether all variables are used after declared.

        There are false-negatives of this policy:

            - g:undeclared_var
            - b:undeclared_var
            - w:undeclared_var
            - t:undeclared_var
            - v:undeclared_var
            - &undeclared_opt
            - a:000[out_of_bound_index]
        """

        is_declared_identifier = self._is_declared_identifier(node)

        return is_declared_identifier


    def _is_ignored_identifier(self, identifier_name):
        # We may get a variable-length parameters token '...' because
        # viml-vimparser can not recognize variable-length parameters.
        # So we should ignore '...' token.
        if identifier_name in '...':
            return True

        # a:0, a:1, ... is implicitly declared parameters
        if re.match(r'a:[0-9]+', identifier_name):
            return True

        return False


    def _is_declared_identifier(self, node):
        identifier_name = node['value']

        # Ignore definition identifiers.
        # See ScopePlugin documents to understand what is definition identifier.
        is_definition_identifier = node[ScopePlugin.DEFINITION_IDENTIFIER_FLAG_KEY]
        if is_definition_identifier:
            return True

        # No prefix identifier is already declared if the identifier is built-in.
        is_builtin_identifier = node[ScopePlugin.BUILTIN_IDENTIFIER_FLAG_KEY]
        if is_builtin_identifier:
            return True

        # Ignore special identifiers such as '...' and 'a:000'
        if self._is_ignored_identifier(identifier_name):
            return True

        scope = node[ScopePlugin.SCOPE_KEY]
        declaration_scope = ScopePlugin.detect_scope(identifier_name, scope)

        traceability_map = ProhibitUsingUndeclaredVariable.identifier_tracability_map
        is_traceable_identifier = traceability_map[declaration_scope]
        if not is_traceable_identifier:
            # Optimistic decision. Expect the identifier is declared by other
            # file.
            return True

        while scope is not None:
            if identifier_name in scope['variables']:
                return True

            scope = scope['parent_scope']

        return False
