import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy


@register_policy
class ProhibitSetNoCompatible(AbstractPolicy):
    def __init__(self):
        super(ProhibitSetNoCompatible, self).__init__()
        self.description = 'Do not use nocompatible which has unexpected effects'
        self.reference = ':help nocompatible'
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.EXCMD]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        This policy prohibit following commands:
         - normal without !
         - substitute
        """

        command = node['str']
        is_nocompatible = re.match(r'set?\s+(?:nocp|invcp|nocompatible|invcompatible)', command)

        return not is_nocompatible
