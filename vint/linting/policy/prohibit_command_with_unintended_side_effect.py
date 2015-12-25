from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from vint.linting.level import Level
from vint.ast.node_type import NodeType
from vint.linting.policy_registry import register_policy


PROHIBITED_COMMAND_PATTERNS = ('substitute',
                               '&',
                               '~',
                               'snomagic',
                               'smagic')


@register_policy
class ProhibitCommandWithUnintendedSideEffect(AbstractPolicy):
    def __init__(self):
        super(ProhibitCommandWithUnintendedSideEffect, self).__init__()
        self.level = Level.WARNING
        self.description = 'Do not use a command that has unintended side effects'
        self.reference = get_reference_source('DANGEROUS')


    def listen_node_types(self):
        return [
            NodeType.EXCMD,
        ]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid to the policy.
        This policy prohibit using `:s[ubstitute]` family.
        """

        command = node['ea']['cmd'].get('name', None)
        is_prohibited_command = any(pattern == command
                                    for pattern in PROHIBITED_COMMAND_PATTERNS)

        return not is_prohibited_command
