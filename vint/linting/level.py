import enum


@enum.unique
class Level(enum.Enum):
    ERROR = 0
    WARNING = 1
    STYLE_PROBLEM = 2


def is_level_enabled(level, base_lebel):
    return level.value <= base_lebel.value
