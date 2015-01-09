from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from vint.linting.level import Level
from vint.ast.node_type import NodeType
from vint.linting.policy_registry import register_policy


GoodStringComparisonOperators = {
    NodeType.EQUAL: ['==#', '==?'],
    NodeType.NEQUAL: ['!=#', '!=?'],
    NodeType.GREATER: ['>#', '>?'],
    NodeType.GEQUAL: ['>=#', '>=?'],
    NodeType.SMALLER: ['<#', '<?'],
    NodeType.SEQUAL: ['<=#', '<=?'],
    NodeType.MATCH: ['=~#', '=~?'],
    NodeType.NOMATCH: ['!~#', '!~?'],
    NodeType.IS: ['is#', 'is?'],
    NodeType.ISNOT: ['isnot#', 'isnot?'],
}


BadStringComparisonOperators = {
    NodeType.EQUAL: '==',
    NodeType.NEQUAL: '!=',
    NodeType.GREATER: '>',
    NodeType.GEQUAL: '>=',
    NodeType.SMALLER: '<',
    NodeType.SEQUAL: '<=',
    NodeType.MATCH: '=~',
    NodeType.NOMATCH: '!~',
    NodeType.IS: 'is',
    NodeType.ISNOT: 'isnot',
}


@register_policy
class ProhibitEqualTildeOperator(AbstractPolicy):
    def __init__(self):
        super(ProhibitEqualTildeOperator, self).__init__()
        self.level = Level.WARNING
        self.description = 'Use the =~# or =~? operator families over the =~ family.'
        self.reference = get_reference_source('MATCHING')


    def listen_node_types(self):
        return [
            NodeType.EQUAL,
            NodeType.NEQUAL,
            NodeType.GREATER,
            NodeType.GEQUAL,
            NodeType.SMALLER,
            NodeType.SEQUAL,
            NodeType.MATCH,
            NodeType.NOMATCH,
            NodeType.IS,
            NodeType.ISNOT,
        ]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid to the policy.

        In this policy, comparing between a string and any value by
        'ignorecase'-sensitive is invalid. This policy can detect following
        script: variable =~ '1'

        But detecting exactly string comparison without evaluation is very hard.
        So this policy often get false-positive/negative results.
            False-positive case is: '1' =~ 1
            False-negative case is: ('1') =~ 1
        """
        node_type = NodeType(node['type'])

        left_type = NodeType(node['left']['type'])
        right_type = NodeType(node['right']['type'])

        is_like_string_comparison = left_type is NodeType.STRING \
            or right_type is NodeType.STRING

        is_valid = not is_like_string_comparison

        if not is_valid:
            self._make_description(node_type)

        return is_valid


    def _make_description(self, node_type):
        good_examples = ['`' + op + '`' for op in GoodStringComparisonOperators[node_type]]
        formatted_good_examples = ' or '.join(good_examples)

        bad_example = BadStringComparisonOperators[node_type]

        params = {
            'good_example': formatted_good_examples,
            'bad_example': bad_example,
        }
        self.description = ('Use robust operators {good_example} '
                            'instead of `{bad_example}`').format(**params)
