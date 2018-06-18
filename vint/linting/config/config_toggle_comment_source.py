from vint.ast.node_type import NodeType
from vint.linting.config.config_abstract_dynamic_source import ConfigAbstractDynamicSource
from vint.linting.config.config_comment_parser import parse_config_comment_node_if_exists


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
        self._config_dict = {'policies': {}}


    def get_config_dict(self):
        return self._config_dict


    def update_by_node(self, node):
        comment_config = parse_config_comment_node_if_exists(node)

        if comment_config is None:
            return

        if comment_config.is_only_next_line:
            # Config comment only affects to next line should be handled by an other class.
            return

        self._config_dict = comment_config.config_dict
