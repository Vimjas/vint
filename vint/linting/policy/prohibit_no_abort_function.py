from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source
from vint.linting.policy_registry import register_policy


@register_policy
class ProhibitNoAbortFunction(AbstractPolicy):
    def __init__(self):
        super(ProhibitNoAbortFunction, self).__init__()
        self.description = 'Use the abort attribute for functions in autoload'
        self.reference = get_reference_source('FUNCTIONS')
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.FUNCTION]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        This policy prohibits functions in autoload that have no 'abort' or bang
        """

        if 'autoload' not in lint_context['path'].parts:
            return True

        has_bang = node['ea']['forceit'] != 0
        has_abort = node['attr']['abort'] != 0

        return has_bang and has_abort
