from vint.ast.node_type import NodeType
from typing import Dict, Any, Optional
import re
CONFIG_COMMENT_PATTERN = re.compile(r'^\s*vint:\s*')
POLICY_SWITCH_PATTERN = re.compile(r'(?:^|\s)[-+]\S+')
NEXT_LINE_FLAG_PATTERN = 'next-line'


class ConfigComment:
    def __init__(self, config_dict, is_only_next_line):
        # type: (Dict[str, Any], bool) -> None
        self.config_dict = config_dict
        self.is_only_next_line = is_only_next_line


def parse_config_comment_node_if_exists(node):
    # type: (Dict[str, Any]) -> Optional[ConfigComment]
    if NodeType(node['type']) is not NodeType.COMMENT:
        return None

    comment_node = node
    comment_content = comment_node['str']

    if not is_config_comment(comment_content):
        return None

    return parse_config_comment(comment_content)


def parse_config_comment(comment_content):
    # type: (str) -> Optional[ConfigComment]

    if not is_config_comment(comment_content):
        return None

    striped_comment_content = CONFIG_COMMENT_PATTERN.sub('', comment_content)

    policy_switches = [policy_switch.strip() for policy_switch in POLICY_SWITCH_PATTERN.findall(striped_comment_content)]
    is_only_next_line = NEXT_LINE_FLAG_PATTERN in striped_comment_content

    policies = {}
    for policy_switch in policy_switches:
        policy_name = policy_switch[1:]
        is_enabling_switch = policy_switch[0] == '+'

        policies[policy_name] = {
            'enabled': is_enabling_switch
        }

    return ConfigComment(
        config_dict={'policies': policies},
        is_only_next_line=is_only_next_line
    )


def is_config_comment(comment_content):
    # type: (str) -> bool
    return CONFIG_COMMENT_PATTERN.match(comment_content) is not None
