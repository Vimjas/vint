import re
from lib.ast.nodetype import NodeType
from lib.linting.level import Levels
from lib.linting.policy.abstract_policy import AbstractPolicy
from lib.linting.policy.reference.googlevimscriptstyleguide import get_reference_source


# see `:help expr-string`
_special_char_matcher = re.compile(
    r'\\('
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
    r')')


class ProhibitUnnecessaryDoubleQuote(AbstractPolicy):
    def __init__(self):
        super().__init__()
        self.description = 'Prefer single quoted strings'
        self.reference = get_reference_source('STRINGS')
        self.level = Levels['WARNING']


    def listen_node_types(self):
        return [NodeType['STRING']]


    def is_valid(self, node, env):
        """ Whether the specified node is valid.

        In this policy, valid node is only 2 cases;
        - single quoted
        - double quoted, but including a special char

        See `:help expr-string`. """

        value = node['value']

        is_double_quoted = value[0] is '"'
        if not is_double_quoted:
            return True

        has_escaped_char = _special_char_matcher.search(value) is not None
        return has_escaped_char
