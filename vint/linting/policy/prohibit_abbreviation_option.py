import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_loader import register_policy
from vint.linting.policy.abbreviation import (
    Abbreviations,
    AbbreviationsIncludingInvertPrefix,
)


@register_policy
class ProhibitAbbreviationOption(AbstractPolicy):
    def __init__(self):
        super(ProhibitAbbreviationOption, self).__init__()
        self.description = 'Use a full option name instead of the abbreviation'
        self.reference = ':help option-summary'
        self.level = Level.WARNING

        self.was_scriptencoding_found = False
        self.has_encoding_opt_after_scriptencoding = False


    def listen_node_types(self):
        return [NodeType.EXCMD, NodeType.OPTION]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        Abbreviation options are invalid.
        """

        node_type = NodeType(node['type'])

        if node_type is NodeType.EXCMD:
            cmd_str = node['str']
            matched = re.match(r':*set?\s+([a-z]+)', cmd_str)
            is_set_cmd = bool(matched)

            if not is_set_cmd:
                return True

            option_name = matched.group(1)
            return option_name not in AbbreviationsIncludingInvertPrefix
        else:
            # Remove & at head
            option_name = node['value'][1:]
            return option_name not in Abbreviations
