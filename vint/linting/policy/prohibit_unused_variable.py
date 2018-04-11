from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.plugin.scope_plugin import ScopeVisibility


@register_policy
class ProhibitUnusedVariable(AbstractPolicy):
    def __init__(self):
        super(ProhibitUnusedVariable, self).__init__()
        self.reference = ':help E738'
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.IDENTIFIER]


    def is_valid(self, identifier, lint_context):
        """ Whether the variables are used.
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
        if not scope_plugin.is_unused_declarative_identifier(identifier):
            return True

        # Ignore global like variables.
        scope_visibility = scope_plugin.get_objective_scope_visibility(identifier)
        if (scope_visibility is ScopeVisibility.GLOBAL_LIKE or
                scope_visibility is ScopeVisibility.BUILTIN or
                scope_visibility is ScopeVisibility.UNANALYZABLE):
            return True

        self.description = 'Unused variable: {var_name}'.format(
            var_name=identifier['value'])
        return False
