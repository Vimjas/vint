import chardet

from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse, SKIP_CHILDREN
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy


@register_policy
class ProhibitMissingScriptEncoding(AbstractPolicy):
    def __init__(self):
        super(ProhibitMissingScriptEncoding, self).__init__()
        self.description = 'Use scriptencoding when multibyte char exists'
        self.reference = ':help :scriptencoding'
        self.level = Level.WARNING

        self.has_scriptencoding = False


    def listen_node_types(self):
        return [NodeType.TOPLEVEL]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        This policy prohibit scriptencoding missing when multibyte char exists.
        """
        traverse(node, on_enter=self._check_scriptencoding)

        if self.has_scriptencoding:
            return True

        return not self._check_script_has_multibyte_char(lint_context)


    def _check_scriptencoding(self, node):
        # TODO: Use BREAK when implemented
        if self.has_scriptencoding:
            return SKIP_CHILDREN

        node_type = NodeType(node['type'])

        if node_type is not NodeType.EXCMD:
            return

        self.has_scriptencoding = node['str'].startswith('scripte')


    def _check_script_has_multibyte_char(self, lint_context):
        # TODO: Use cache to make performance efficiency
        with lint_context['path'].open(mode='br') as f:
            byte_seq = f.read()
        return len(byte_seq) and chardet.detect(byte_seq)['encoding'] != 'ascii'
