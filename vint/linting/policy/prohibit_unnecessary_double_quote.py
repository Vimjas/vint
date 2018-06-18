import re
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.map_and_filter_parser import get_string_context
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from vint.linting.policy_registry import register_policy



# see `:help expr-string`
_special_char_matcher = re.compile(
    r'(\'|'  # allow single quote
    r'\\('  # prefix back slash
    r'(?P<octal>[0-7]{1,3})'
    r'|(?P<hexadecimal>[xX][0-9a-fA-F]{1,2})'
    r'|(?P<numeric_character_reference>[uU][0-9a-fA-F]{4})'
    r'|(?P<backspace>b)'
    r'|(?P<escape>e)'
    r'|(?P<form_feed>f)'
    r'|(?P<new_line>n)'
    r'|(?P<carriage_return>r)'
    r'|(?P<tab>t)'
    r'|(?P<backslash>\\)'
    r'|(?P<double_quote>")'
    r'|(?P<special_key><[^>]+>)'
    r'))')


@register_policy
class ProhibitUnnecessaryDoubleQuote(AbstractPolicy):
    def __init__(self):
        super(ProhibitUnnecessaryDoubleQuote, self).__init__()
        self.description = 'Prefer single quoted strings'
        self.reference = get_reference_source('STRINGS')
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.STRING]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        In this policy, valid node is only 2 cases;
        - single quoted
        - double quoted, but including a special char

        See `:help expr-string`. """

        value = node['value']

        is_double_quoted = value[0] == '"'
        if not is_double_quoted:
            return True

        has_escaped_char = _special_char_matcher.search(value) is not None

        if has_escaped_char:
            return True

        string_expr_context = get_string_context(node)
        return string_expr_context['is_on_str_expr_context']
