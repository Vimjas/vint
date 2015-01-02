import enum
from vint.ast.node_type import NodeType
from vint.ast.dictionary.builtins import (
    BuiltinVariables,
    BuiltinFunctions,
)
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    is_identifier_like_node,
    is_dynamic_identifier,
    is_declarative_identifier,
    is_function_identifier,
    is_member_identifier,
    is_autoload_identifier,
)


class ScopeVisibility(enum.Enum):
    """ 5 types scope visibility.
    We interest to analyze the variable scope by checking a single file.
    So, we do not interest to the strict visibility of the scopes that have a
    larger visibility than script local.
    """
    GLOBAL_LIKE = 0
    BUILTIN = 1
    SCRIPT_LOCAL = 2
    FUNCTION_LOCAL = 3
    UNANALYZABLE = 4


IdentifierScopePrefixToScopeVisibility = {
    'g:': ScopeVisibility.GLOBAL_LIKE,
    'b:': ScopeVisibility.GLOBAL_LIKE,
    'w:': ScopeVisibility.GLOBAL_LIKE,
    't:': ScopeVisibility.GLOBAL_LIKE,
    's:': ScopeVisibility.SCRIPT_LOCAL,
    'l:': ScopeVisibility.FUNCTION_LOCAL,
    'a:': ScopeVisibility.FUNCTION_LOCAL,
    'v:': ScopeVisibility.BUILTIN,
}


ImplicitScopeVisibilityToIdentifierScopePrefix = {
    ScopeVisibility.GLOBAL_LIKE: 'g:',
    ScopeVisibility.FUNCTION_LOCAL: 'l:',
    ScopeVisibility.BUILTIN: 'v:',
}


GlobalLikeScopeVisibilityNodeTypes = {
    NodeType.ENV: True,
    NodeType.OPTION: True,
    NodeType.REG: True,
}


IdentifierLikeNodeTypes = {
    NodeType.IDENTIFIER: True,
    NodeType.ENV: True,
    NodeType.OPTION: True,
    NodeType.REG: True,
}


def is_builtin_variable(id_node):
    """ Whether the specified node is a builtin identifier. """
    if not is_identifier_like_node(id_node):
        return False

    id_value = id_node['value']
    if id_value.startswith('v:'):
        # It is an explicit builtin variable such as: "v:count", "v:char"
        # TODO: Add unknown builtin flag
        return True

    if is_function_identifier(id_node):
        # There are defference between a function identifier and variable
        # identifier:
        #
        #   let localtime = 0
        #   echo localtime " => 0
        #   echo localtime() " => 1420011455
        return id_value in BuiltinFunctions

    # It is an implicit builtin variable such as: "count", "char"
    return id_value in BuiltinVariables


def is_builtin_function(id_node):
    """ Whether the specified node is a builtin function name identifier.
    The given identifier should be a child node of NodeType.CALL.
    """
    id_value = id_node['value']
    return id_value in BuiltinFunctions


def is_analyzable_identifier(node):
    """ Whether the specified node is an analyzable identifier.

    Node declarative-identifier-like is analyzable if it is not dynamic
    and not a member variable, because we can do static scope analysis.

    Analyzable cases:
      - let s:var = 0
      - function! Func()
      - echo s:var

    Unanalyzable cases:
      - let s:my_{var} = 0
      - function! dict.Func()
      - echo s:my_{var}
    """
    return not (is_dynamic_identifier(node) or is_member_identifier(node))


def is_analyzable_declarative_identifier(node):
    """ Whether the specified node is an analyzable declarative identifier.
    Node declarative-identifier-like is analyzable if it is not dynamic
    and not a member variable, because we can do static scope analysis.

    Analyzable cases:
      - let s:var = 0
      - function! Func()

    Unanalyzable cases:
      - let s:my_{var} = 0
      - function! dict.Func()
    """
    return is_declarative_identifier(node) and is_analyzable_identifier(node)


def detect_scope_visibility(node, context_scope):
    """ Returns a variable visibility hint by the specified node.
    The hint is a dict that has 2 attributes: "scope_visibility" and
    "is_implicit".
    """
    node_type = NodeType(node['type'])

    if not is_analyzable_identifier(node):
        return _create_identifier_visibility_hint(ScopeVisibility.UNANALYZABLE)

    if node_type is NodeType.IDENTIFIER:
        return _detect_identifier_scope_visibility(node, context_scope)

    if node_type in GlobalLikeScopeVisibilityNodeTypes:
        return _create_identifier_visibility_hint(ScopeVisibility.GLOBAL_LIKE)


def normalize_variable_name(node, context_scope):
    """ Returns normalized variable name.
    Normalizing means that variable names get explicit visibility by
    visibility prefix such as: "g:", "s:", ...

    Retunes None if the specified node is unanalyzable.
    A node is unanalyzable if:

    - the node is not identifier-like
    - the node is named dynamically
    """
    node_type = NodeType(node['type'])

    if not is_analyzable_identifier(node):
        return None

    if node_type is NodeType.IDENTIFIER:
        return _normalize_identifier_value(node, context_scope)

    # Nodes identifier-like without identifier is always normalized because
    # the nodes can not have a visibility prefix.
    if node_type in IdentifierLikeNodeTypes:
        return node['value']


def _normalize_identifier_value(id_node, context_scope):
    scope_visibility_hint = detect_scope_visibility(id_node, context_scope)

    if not scope_visibility_hint['is_implicit']:
        return id_node['value']

    scope_visibility = scope_visibility_hint['scope_visibility']
    scope_prefix = ImplicitScopeVisibilityToIdentifierScopePrefix[scope_visibility]

    return scope_prefix + id_node['value']


def _detect_identifier_scope_visibility(id_node, context_scope):
    id_value = id_node['value']

    explicit_scope_visibility = _get_explicit_scope_visibility(id_value)
    if explicit_scope_visibility is not None:
        return _create_identifier_visibility_hint(explicit_scope_visibility)

    # Implicit scope variable will be resolved as a builtin variable if it
    # has a same name to Vim builtin variables.
    if is_builtin_variable(id_node):
        return _create_identifier_visibility_hint(ScopeVisibility.BUILTIN,
                                                  is_implicit=True)

    # Only autoload functions implicity declared are always on global.
    # For example:
    #
    #   " in autoload/file.vim
    #   let file#var = 0
    #   function file#func()
    #     return 1
    #   endfunction
    #
    #
    #   " in anywhere using autoload
    #   function FuncContext()
    #     " ok
    #     echo g:file#func()
    #     echo g:file#var
    #     echo file#func()
    #
    #     " ng
    #     echo file#var
    #   endfunction
    #   call FuncContext()
    if is_function_identifier(id_node) and is_autoload_identifier(id_node):
        return _create_identifier_visibility_hint(ScopeVisibility.GLOBAL_LIKE,
                                                  is_implicit=True)

    if not context_scope:
        # We cannot detect implicit scope visibility if context scope is not
        # specified.
        return _create_identifier_visibility_hint(ScopeVisibility.UNANALYZABLE)

    # Implicit scope variable will be resolved as a global variable when
    # current scope is script local. Otherwise be a function local variable.
    current_scope_visibility = context_scope['scope_visibility']
    if current_scope_visibility is ScopeVisibility.SCRIPT_LOCAL:
        return _create_identifier_visibility_hint(ScopeVisibility.GLOBAL_LIKE,
                                                  is_implicit=True)

    return _create_identifier_visibility_hint(ScopeVisibility.FUNCTION_LOCAL,
                                              is_implicit=True)


def _get_explicit_scope_visibility(id_value):
    # See :help internal-variables
    scope_prefix = id_value[0:2]
    return IdentifierScopePrefixToScopeVisibility.get(scope_prefix, None)


def _create_identifier_visibility_hint(visibility, is_implicit=False):
    return {
        'scope_visibility': visibility,
        'is_implicit': is_implicit,
    }
