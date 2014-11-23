from enum import Enum


class VariableType(Enum):
    GLOBAL = 1
    BUFFER_LOCAL = 2
    WINDOW_LOCAL = 3
    TAB_LOCAL = 4
    SCRIPT_LOCAL = 5
    FUNCTION_LOCAL = 6
    PARAMETER = 7
    BUILTIN = 8
