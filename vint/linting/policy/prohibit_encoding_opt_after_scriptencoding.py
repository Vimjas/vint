import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy


@register_policy
class ProhibitEncodingOptionAfterScriptEncoding(AbstractPolicy):
    description = 'Set encoding before setting scriptencoding'
    reference = ':help :scriptencoding'
    level = Level.WARNING

    was_scriptencoding_found = False
    has_encoding_opt_after_scriptencoding = False


    def listen_node_types(self):
        return [NodeType.EXCMD]


    def is_valid(self, excmd_node, lint_context):
        """ Whether the specified node is valid.

        This policy prohibits encoding option after scriptencoding.
        """

        cmd_str = excmd_node['str']

        if re.match(r':*scripte', cmd_str):
            self.was_scriptencoding_found = True

        if re.match(r':*set? +enc', cmd_str) and self.was_scriptencoding_found:
            return False

        return True
