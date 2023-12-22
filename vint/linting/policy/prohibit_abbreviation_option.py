import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.dictionary.abbreviations import (
    Abbreviations,
    AbbreviationsIncludingInvertPrefix,
)


SetCommandFamily = {
    'set': True,
    'setlocal': True,
    'setglobal': True,
}


@register_policy
class ProhibitAbbreviationOption(AbstractPolicy):
    description = 'Use the full option name instead of the abbreviation'
    reference = ':help option-summary'
    level = Level.STYLE_PROBLEM


    def listen_node_types(self):
        return [NodeType.EXCMD, NodeType.OPTION]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        Abbreviation options are invalid.
        """

        node_type = NodeType(node['type'])

        if node_type is NodeType.OPTION:
            # Remove & at head
            option_name = node['value'][1:]
            is_valid = option_name not in Abbreviations

            if not is_valid:
                self._make_description_by_option_name(option_name)

            return is_valid

        excmd_node = node
        is_set_cmd = excmd_node['ea']['cmd'].get('name') in SetCommandFamily

        if not is_set_cmd:
            return True

        option_expr = excmd_node['str'].split()[1]
        # Care `:set ft=vim` and `:set cpo&vim`, ...
        option_name = re.match(r'[a-z]+', option_expr).group(0)

        # After a "set" command, we can add an invert prefix "no" and "inv"
        # to options. For example, "nowrap" is an inverted option "wrap".
        is_valid = option_name not in AbbreviationsIncludingInvertPrefix

        if not is_valid:
            self._make_description_by_option_name(option_name)

        return is_valid


    def _make_description_by_option_name(self, option_name):
        param = {
            'good_pattern': AbbreviationsIncludingInvertPrefix[option_name],
            'bad_pattern': option_name,
        }

        self.description = ('Use the full option name `{good_pattern}` '
                            'instead of `{bad_pattern}`'.format(**param))
