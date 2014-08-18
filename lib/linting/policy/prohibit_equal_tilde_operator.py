from lib.linting.policy.abstract_policy import AbstractPolicy
from lib.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from lib.linting.level import Level
from lib.ast.node_type import NodeType


class ProhibitEqualTildeOperator(AbstractPolicy):
    def __init__(self):
        super().__init__()
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


    def is_valid(self, node, env):
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

        if node_type is NodeType.MATCH or node_type is NodeType.NOMATCH:
            return False

        left_type = NodeType(node['left']['type'])
        right_type = NodeType(node['right']['type'])

        is_like_string_comparison = left_type is NodeType.STRING or right_type is NodeType.STRING
        return not is_like_string_comparison
