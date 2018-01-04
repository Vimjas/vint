from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy


@register_policy
class ProhibitInvalidMapCall(AbstractPolicy):
    def __init__(self):
        super(ProhibitInvalidMapCall, self).__init__()
        self.description = 'Number of arguments for map() must be 2 (if not, it will throw E118 or E119)'
        self.reference = ':help map()'
        self.level = Level.ERROR


    def listen_node_types(self):
        return [NodeType.CALL]


    def is_valid(self, node, lint_context):
        left_node = node['left']

        if NodeType(left_node['type']) != NodeType.IDENTIFIER:
            return True

        if left_node['value'] != 'map':
            return True

        args = node['rlist']
        return len(args) == 2
