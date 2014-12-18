from enum import Enum


class Level(Enum):
    ERROR = 0
    WARNING = 1
    STYLE_PROBLEM = 2


def is_level_enabled(level, config_dict):
    return level.value <= config_dict['severity'].value
