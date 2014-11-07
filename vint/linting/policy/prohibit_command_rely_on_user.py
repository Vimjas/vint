import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from vint.linting.policy_loader import register_policy


PROHIBITED_COMMAND_PATTERN = re.compile(r'norm(al)?\s|'
                                        r's(u(bstitute)?)?/')


@register_policy
class ProhibitCommandRelyOnUser(AbstractPolicy):
    def __init__(self):
        super(ProhibitCommandRelyOnUser, self).__init__()
        self.description = 'Prefer single quoted strings'
        self.reference = get_reference_source('FRAGILE')
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
        is_command_not_prohibited = PROHIBITED_COMMAND_PATTERN.search(command) is None

        return is_command_not_prohibited
