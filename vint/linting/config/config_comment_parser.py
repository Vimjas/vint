import re
CONFIG_COMMENT_PATTERN = re.compile(r'^\s*vint:\s*')
POLICY_SWITCH_PATTERN = re.compile(r'[-+]\S+')


def parse_config_comment(comment_content):
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


def is_config_comment(comment_content):
    return CONFIG_COMMENT_PATTERN.match(comment_content) is not None

