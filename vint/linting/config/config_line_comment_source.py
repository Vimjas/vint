from typing import Dict, Any
from vint.ast.plugin.annotation_comment_plugin import get_postfix_comment
from vint.linting.config.config_abstract_dynamic_source import ConfigAbstractDynamicSource
from vint.linting.config.config_comment_parser import (
    parse_config_comment,
    is_config_comment,
)


class ConfigLineCommentSource(ConfigAbstractDynamicSource):
    """ A class for ConfigLineCommentSources.
    This class provide to change config by modeline-like config comments as
    follow:

        call s:foo() " vint: -PolicyA
        call s:foo() " vint: +PolicyA
        call s:foo() " vint: -PolicyA +PolicyB

    Prefix vint: means that the comment is a config comment. And, +PolicyName
    means to enable the policy, and -PolicyName means to disable.

    This class handle the config comment that have before nodes at the line. For example:

        echo 'Vint do not check the code before the comment' " vint: -PolicyA
        echo 'Vint check the code'
    """
    def __init__(self):
        super(ConfigLineCommentSource, self).__init__()

        self._parse_result_cache = {}  # type: Dict[int, Dict[str, Any]]
        self._config_dict = {
            'policies': {},
        }


    def get_config_dict(self):
        return self._config_dict


    def update_by_node(self, node):
        postfix_comment_node = get_postfix_comment(node)

        has_line_config_comment = postfix_comment_node is not None and \
                                  is_config_comment(postfix_comment_node['str'])
        if not has_line_config_comment:
            self._config_dict = {'policies': {}}
            return

        postfix_comment_node = get_postfix_comment(node)
        postfix_comment_node_id = id(postfix_comment_node)

        if postfix_comment_node_id in self._parse_result_cache:
            parse_result = self._parse_result_cache[postfix_comment_node_id]
        else:
            parse_result = parse_config_comment(postfix_comment_node['str'])
            self._parse_result_cache[postfix_comment_node_id] = parse_result

        self._config_dict = {'policies': parse_result}
