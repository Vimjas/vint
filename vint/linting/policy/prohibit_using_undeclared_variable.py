from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.plugin.scope_plugin import ScopeVisibility


@register_policy
class ProhibitUsingUndeclaredVariable(AbstractPolicy):
    def __init__(self):
        super(ProhibitUsingUndeclaredVariable, self).__init__()
        self.description = 'Variable is not declared'
        self.reference = ':help E738'
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.IDENTIFIER]


    def is_valid(self, identifier, lint_context):
        """ Whether all variables are used after declared.
        This policy cannot determine the following node types:
          - Global identifier like nodes
            - ENV
            - REG
            - OPTION
          - Dynamic variables
            - CURLYNAME
            - SLICE
            - DOT
            - SUBSCRIPT
        """

        scope_plugin = lint_context['plugins']['scope']
        is_reachable = not scope_plugin.is_unreachable_reference_identifier(identifier)

        scope_visibility = scope_plugin.get_objective_scope_visibility(identifier)
        is_global = scope_visibility is ScopeVisibility.GLOBAL_LIKE
        is_builtin = scope_visibility is ScopeVisibility.BUILTIN
        is_unanalyzable = scope_visibility is ScopeVisibility.UNANALYZABLE

        # Ignore global like variables
        is_valid = is_reachable or is_global or is_builtin or is_unanalyzable

        if not is_valid:
            self._make_description(identifier)

        return is_valid


    def _make_description(self, identifier):
        self.description = 'Undefined variable: {var_name}'.format(
            var_name=identifier['value'])
