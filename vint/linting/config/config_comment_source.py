import re
from vint.linting.config.config_source import ConfigSource
from vint.ast.node_type import NodeType

CONFIG_COMMENT_PATTERN = re.compile(r'^\s*vint:\s*')
POLICY_SWITCH_PATTERN = re.compile(r'[-\+]\S+')


class ConfigCommentSource(ConfigSource):
    """ A class for ConfigCommentSourcees.
    This class provide to change config by modeline-like config comments as
    follow:

        " vint: -PolicyA
        " vint: +PolicyA
        " vint: -PolicyA +PolicyB

    Prefix vint: means that the comment is a config comment. And, +PolicyName
    means to enable the policy, and -PolicyName means to disable.
    """
    def __init__(self):
        self._config_dict = {
            'policies': {}
        }


    def get_config_dict(self):
        return self._config_dict


    def is_requesting_update(self, node):
        return self._is_config_comment(node)


    def update_by_node(self, node):
        comment_content = node['str']

        config_dict = self._config_dict
        config_dict['policies'] = self._parse_config_comment(comment_content)


    def _is_config_comment(self, node):
        if NodeType(node['type']) is not NodeType.COMMENT:
            return False

        comment_content = node['str']
        return CONFIG_COMMENT_PATTERN.match(comment_content) is not None


    def _parse_config_comment(self, comment_content):
        striped_comment_content = CONFIG_COMMENT_PATTERN.sub('', comment_content)

        policy_switches = POLICY_SWITCH_PATTERN.findall(striped_comment_content)

        config_dict = {}
        for policy_switch in policy_switches:
            policy_name = policy_switch[1:]
            is_enabling_switch = policy_switch[0] == '+'

            config_dict[policy_name] = {
                'enabled': is_enabling_switch
            }

        return config_dict
