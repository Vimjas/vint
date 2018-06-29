import logging
from typing import Dict, Any
from vint.linting.config.config_abstract_dynamic_source import ConfigAbstractDynamicSource
from vint.linting.config.config_comment_parser import parse_config_comment_node_if_exists


class ConfigNextLineCommentSource(ConfigAbstractDynamicSource):
    """ A class for ConfigLineCommentSources.
    This class provide to change config by modeline-like config comments as
    follow:

        " vint: next-line -PolicyA
        " vint: next-line +PolicyA
        " vint: next-line -PolicyA +PolicyB

    Prefix vint: means that the comment is a config comment. And, +PolicyName
    means to enable the policy, and -PolicyName means to disable.

    This class handle the config comment that have before nodes at the line. For example:

        " vint: next-line -PolicyA
        echo 'Vint do not check the code after the comment'
        echo 'Vint check the code'
    """
    def __init__(self, is_debug=False):
        super(ConfigNextLineCommentSource, self).__init__()

        self._is_debug = is_debug
        self._current_lnum = 0
        self._empty_config_dict = {
            'policies': {},
            'source_name': self.__class__.__name__,
        }  # type: Dict[str, Any]
        self._config_dict = self._empty_config_dict
        self._config_dict_for_next_line = self._empty_config_dict


    def get_config_dict(self):
        return self._config_dict


    def update_by_node(self, node):
        lnum_of_node = node['pos']['lnum']
        is_line_changed = lnum_of_node > self._current_lnum

        if is_line_changed:
            if lnum_of_node - self._current_lnum == 1:
                if self._is_debug and self._config_dict != self._config_dict_for_next_line:
                    logging.debug("{cls}: update config to {config_dict} at {lnum}".format(
                        cls=self.__class__.__name__,
                        config_dict=self._config_dict_for_next_line,
                        lnum=lnum_of_node
                    ))

                self._config_dict = self._config_dict_for_next_line
            else:
                if self._is_debug and self._config_dict != self._empty_config_dict:
                    logging.debug("{cls}: update config to {config_dict} at {lnum}".format(
                        cls=self.__class__.__name__,
                        config_dict=self._empty_config_dict,
                        lnum=lnum_of_node
                    ))

                self._config_dict = self._empty_config_dict

            # Refresh config_dict for each line.
            self._current_lnum = lnum_of_node
            self._config_dict_for_next_line = self._empty_config_dict

        config_comment = parse_config_comment_node_if_exists(node)

        if config_comment is None:
            return

        if not config_comment.is_only_next_line:
            # Config comment affects over lines should be handled by an other class.
            return

        self._config_dict_for_next_line = config_comment.config_dict
        self._config_dict_for_next_line['source_name'] = self.__class__.__name__
