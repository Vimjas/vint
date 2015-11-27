from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from vint.linting.policy_registry import register_policy


ProhibitedCommands = {
    'substitute': True,
}

CommandsShouldBeWithBang = {
    'normal': True,
}


@register_policy
class ProhibitCommandRelyOnUser(AbstractPolicy):
    def __init__(self):
        super(ProhibitCommandRelyOnUser, self).__init__()
        self.description = 'Avoid commands that rely on user settings'
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

        ea = node['ea']
        command = ea['cmd'].get('name', None)

        # It seems line jump command
        if command is None:
            return True

        is_prohibited_command = command in ProhibitedCommands
        if is_prohibited_command:
            return False

        should_be_with_bang = command in CommandsShouldBeWithBang
        if not should_be_with_bang:
            return True

        is_bang = ea.get('forceit', 0) == 1
        return is_bang
