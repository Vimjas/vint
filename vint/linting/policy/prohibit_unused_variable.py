import re
import logging
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.plugin.scope_plugin import ScopeVisibility


@register_policy
class ProhibitUnusedVariable(AbstractPolicy):
    reference = ':help E738'
    level = Level.WARNING


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

        identifier_value = identifier['value']

        # Ignore the violation when the name is specified by "policies.ProhibitUnusedVariable.ignored_patterns".
        ignored_patterns = self.get_policy_config(lint_context).get("ignored_patterns", [])
        for ignored_pattern in ignored_patterns:
            if re.search(ignored_pattern, identifier_value) is not None:
                logging.debug("{policy_name}: {name} is unused but ignored by the ignored_pattern {ignored_pattern}.".format(
                    policy_name=self.__class__.__name__,
                    name=identifier_value,
                    ignored_pattern=ignored_pattern
                ))
                return True

        if scope_plugin.is_function_identifier(identifier):
            node_type = 'function'
        else:
            node_type = 'variable'
        self.description = 'Unused {node_type}: {var_name}'.format(node_type = node_type, var_name=identifier_value)
        return False
