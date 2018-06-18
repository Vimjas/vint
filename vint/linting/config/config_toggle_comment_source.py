from typing import Dict, Any
import logging
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

        self._config_dict = {
            'policies': {},
            'source_name': self.__class__.__name__,
        }  # type: Dict[str, Any]


    def get_config_dict(self):
        return self._config_dict


    def update_by_node(self, node):
        config_comment = parse_config_comment_node_if_exists(node)

        if config_comment is None:
            return

        if config_comment.is_only_next_line:
            # Config comment only affects to next line should be handled by an other class.
            return

        logging.debug("{cls}: update config to {config_dict} at {lnum}".format(
            cls=self.__class__.__name__,
            config_dict=config_comment.config_dict,
            lnum=node['pos']['lnum']
        ))

        self._config_dict = config_comment.config_dict
        self._config_dict['source_name'] = self.__class__.__name__
