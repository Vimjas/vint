from enum import Enum
from vint.ast.plugin.scope_plugin.scope_type import ScopeType


class VariableType(Enum):
    GLOBAL = 1
    BUFFER_LOCAL = 2
    WINDOW_LOCAL = 3
    TAB_LOCAL = 4
    SCRIPT_LOCAL = 5
    FUNCTION_LOCAL = 6
    PARAMETER = 7
    BUILTIN = 8


IdentifierPrefixOfVariableType = {
    'g:': VariableType.GLOBAL,
    'b:': VariableType.BUFFER_LOCAL,
    'w:': VariableType.WINDOW_LOCAL,
    't:': VariableType.TAB_LOCAL,
    's:': VariableType.SCRIPT_LOCAL,
    'l:': VariableType.FUNCTION_LOCAL,
    'a:': VariableType.PARAMETER,
    'v:': VariableType.BUILTIN,
}


def is_implicit_variable_type(identifier_name):
    # No declaration scope means implicit declaration.
    return detect_explicit_scope(identifier_name) is None


def detect_variable_type(identifier_name, scope):
    if is_implicit_variable_type(identifier_name):
        return detect_implicit_scope(identifier_name, scope)
    else:
        return detect_explicit_scope(identifier_name)


def detect_explicit_scope(identifier_name):
    """ Returns a VariableType by the specified identifier name.
    Return None when the variable have no scope-prefix.
    """

    # See:
    #   :help let-&
    #   :help let-$
    #   :help let-@
    first_char = identifier_name[0]
    if first_char in '&$@':
        return VariableType.GLOBAL

    # See:
    #   :help E738
    prefix = identifier_name[0:2]
    if prefix in IdentifierPrefixOfVariableType:
        return IdentifierPrefixOfVariableType[prefix]

    # It is GLOBAL or FUNCTION_LOCAL, but we cannot determine without the
    # parent scope.
    return None


def detect_implicit_scope(identifier_name, scope):
    is_toplevel_context = scope['type'] is ScopeType.TOPLEVEL

    # See :help internal-variables
    # > In a function: local to a function; otherwise: global
    if is_toplevel_context:
        return VariableType.GLOBAL
    else:
        return VariableType.FUNCTION_LOCAL
