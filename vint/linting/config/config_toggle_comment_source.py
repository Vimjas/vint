from vint.ast.node_type import NodeType
from vint.ast.plugin.annotation_comment_plugin import is_postfix_comment
from vint.linting.config.config_abstract_dynamic_source import ConfigAbstractDynamicSource
from vint.linting.config.config_comment_parser import (
    parse_config_comment,
    is_config_comment,
)


class ConfigToggleCommentSource(ConfigAbstractDynamicSource):
    """ A class for ConfigToggleCommentSources.
    This class provide to change config by modeline-like config comments as
    follow:

        " vint: -PolicyA
        " vint: +PolicyA
        " vint: -PolicyA +PolicyB

    The prefix 'vint:' means that the comment is a config comment. And, +PolicyName
    means to enable the policy, and -PolicyName means to disable.

    This class handle the config comment that have no before nodes at the line. For example:

        " vint: -PolicyA
        echo 'Vint do not check the code after the above comment'
        " vint: +PolicyA
        echo 'Vint check the code after the above comment'
    """
    def __init__(self):
        super(ConfigToggleCommentSource, self).__init__()
        self._config_dict = {
            'policies': {},
        }


    def get_config_dict(self):
        return self._config_dict


    def update_by_node(self, node):
        if not ConfigToggleCommentSource._is_toggle_config_comment(node):
            return

        comment_content = node['str']

        config_dict = self._config_dict
        config_dict['policies'] = parse_config_comment(comment_content)


    @classmethod
    def _is_toggle_config_comment(cls, node):
        if NodeType(node['type']) is not NodeType.COMMENT:
            return False

        if is_postfix_comment(node):
            # This is a line config comment, not a toggle config comment.
            return False

        return is_config_comment(node['str'])
