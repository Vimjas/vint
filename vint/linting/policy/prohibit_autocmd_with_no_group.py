import re
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.dictionary.autocmd_events import AutocmdEvents
from vint.ast.plugin.autocmd_parser import AUTOCMD_CONTENT
from pprint import pprint


@register_policy
class ProhibitAutocmdWithNoGroup(AbstractPolicy):
    def __init__(self):
        super(ProhibitAutocmdWithNoGroup, self).__init__()
        self.description = 'autocmd should execute in an augroup or execute with a group'
        self.reference = ':help :autocmd'
        self.level = Level.WARNING

        self.is_inside_of_augroup = False


    def listen_node_types(self):
        return [NodeType.EXCMD]


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid.

        autocmd family should be called with any groups.
        """

        # node.ea.cmd is empty when line jump command such as 1
        cmd_name = node['ea']['cmd'].get('name', None)

        is_autocmd = cmd_name == 'autocmd'
        if is_autocmd and not self.is_inside_of_augroup:
            autocmd_attr = node[AUTOCMD_CONTENT]
            if autocmd_attr['bang']:
                # Looks like autocmd with a bang
                return True

            has_group = autocmd_attr.get('group') is not None
            if has_group:
                return True

            return self.is_inside_of_augroup

        is_augroup = cmd_name == 'augroup'
        if is_augroup:
            matched = re.match(r'aug(?:roup)?\s+END', node['str'])
            is_augroup_end = bool(matched)
            self.is_inside_of_augroup = not is_augroup_end

        return True
