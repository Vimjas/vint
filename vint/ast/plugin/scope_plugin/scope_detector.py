from typing import Dict, Any, Optional
from vint.ast.plugin.scope_plugin.scope import (
    ScopeVisibility,
    ExplicityOfScopeVisibility,
    Scope,
)
from vint.ast.node_type import NodeType
from vint.ast.dictionary.builtins import (
    BuiltinVariablesCanHaveImplicitScope,
    BuiltinFunctions,
)
from vint.ast.plugin.scope_plugin.identifier_attribute import (
    is_dynamic_identifier,
    is_declarative_identifier,
    is_function_identifier,
    is_member_identifier,
    is_on_lambda_string_context,
    is_lambda_argument_identifier,
    is_function_argument,
)


class ScopeVisibilityHint:
    def __init__(self, scope_visibility, explicity):
        # type: (ScopeVisibility, ExplicityOfScopeVisibility) -> None
        self.scope_visibility = scope_visibility
        self.explicity = explicity


FunctionDeclarationIdentifierScopePrefixToScopeVisibility = {
    'g:': ScopeVisibility.GLOBAL_LIKE,
    'b:': ScopeVisibility.INVALID,
    'w:': ScopeVisibility.INVALID,
    't:': ScopeVisibility.INVALID,
    's:': ScopeVisibility.SCRIPT_LOCAL,
    'l:': ScopeVisibility.INVALID,
    'a:': ScopeVisibility.INVALID,
    'v:': ScopeVisibility.INVALID,
}


VariableIdentifierScopePrefixToScopeVisibility = {
    'g:': ScopeVisibility.GLOBAL_LIKE,
    'b:': ScopeVisibility.GLOBAL_LIKE,
    'w:': ScopeVisibility.GLOBAL_LIKE,
    't:': ScopeVisibility.GLOBAL_LIKE,
    's:': ScopeVisibility.SCRIPT_LOCAL,
    'l:': ScopeVisibility.FUNCTION_LOCAL,
    'a:': ScopeVisibility.FUNCTION_LOCAL,
    'v:': ScopeVisibility.BUILTIN,
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


def is_builtin_variable(id_node): # type: (Dict[str, Any]) -> bool
    """ Whether the specified node is a builtin identifier. """
    # Builtin variables are always IDENTIFIER.
    if NodeType(id_node['type']) is not NodeType.IDENTIFIER:
        return False

    id_value = id_node['value']

    if id_value.startswith('v:'):
        # It is an explicit builtin variable such as: "v:count", "v:char"
        # TODO: Add unknown builtin flag
        return True

    if is_builtin_function(id_node):
        return True

    if id_value in ['key', 'val']:
        # These builtin variable names are available on only map() or filter().
        return is_on_lambda_string_context(id_node)

    # It is an implicit builtin variable such as: "count", "char"
    return id_value in BuiltinVariablesCanHaveImplicitScope


def is_builtin_function(id_node): # type: (Dict[str, Any]) -> bool
    """ Whether the specified node is a builtin function name identifier.
    The given identifier should be a child node of NodeType.CALL.
    """
    # Builtin functions are always IDENTIFIER.
    if NodeType(id_node['type']) is not NodeType.IDENTIFIER:
        return False

    id_value = id_node['value']

    if not is_function_identifier(id_node):
        return False

    # There are difference between a function identifier and variable
    # identifier:
    #
    #   let localtime = 0
    #   echo localtime " => 0
    #   echo localtime() " => 1420011455
    return id_value in BuiltinFunctions


def is_analyzable_identifier(node): # type: (Dict[str, Any]) -> bool
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


def is_analyzable_declarative_identifier(node): # type: (Dict[str, Any]) -> bool
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


def detect_possible_scope_visibility(node, context_scope): # type: (Dict[str, Any], Scope) -> ScopeVisibilityHint
    """ Returns a *possible* variable visibility by the specified node.
    The "possible" means that we can not determine a scope visibility of lambda arguments until reachability check.
    """
    node_type = NodeType(node['type'])

    if not is_analyzable_identifier(node):
        return ScopeVisibilityHint(
            ScopeVisibility.UNANALYZABLE,
            ExplicityOfScopeVisibility.UNANALYZABLE
        )

    if node_type is NodeType.IDENTIFIER:
        return _detect_possible_identifier_scope_visibility(node, context_scope)

    if node_type in GlobalLikeScopeVisibilityNodeTypes:
        return ScopeVisibilityHint(
            ScopeVisibility.GLOBAL_LIKE,
            ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED
        )

    return ScopeVisibilityHint(
        ScopeVisibility.UNANALYZABLE,
        ExplicityOfScopeVisibility.UNANALYZABLE
    )


def _detect_possible_identifier_scope_visibility(id_node, context_scope):
    # type: (Dict[str, Any], Scope) -> ScopeVisibilityHint
    explicit_scope_visibility = _get_explicit_scope_visibility(id_node)
    if explicit_scope_visibility is not None:
        # Vim allow `g:` as a function name prefix but it is not recommended.
        # SEE: https://github.com/Kuniwak/vint/pull/136
        is_unrecommended_explicit = is_function_identifier(id_node) and _is_just_global(id_node)
        if is_unrecommended_explicit:
            return ScopeVisibilityHint(
                explicit_scope_visibility,
                ExplicityOfScopeVisibility.UNRECOMMENDED_EXPLICIT
            )

        return ScopeVisibilityHint(
            explicit_scope_visibility,
            ExplicityOfScopeVisibility.EXPLICIT
        )

    if is_function_argument(id_node):
        # Function arguments can not have any explicit scope prefix.
        return ScopeVisibilityHint(
            ScopeVisibility.FUNCTION_LOCAL,
            ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED
        )

    if is_builtin_function(id_node):
        # Builtin functions can not have any scope prefix.
        return ScopeVisibilityHint(
            ScopeVisibility.BUILTIN,
            ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED
        )

    if is_builtin_variable(id_node):
        # Implicit scope variable will be resolved as a builtin variable if it
        # has a same name to Vim builtin variables.
        return ScopeVisibilityHint(
            ScopeVisibility.BUILTIN,
            ExplicityOfScopeVisibility.IMPLICIT
        )

    if is_function_identifier(id_node):
        # Functions can have the scope visibility only explicit global or
        # implicit global or explicit script local. So a function have implicit
        # scope visibility is always a global function.
        #
        # And the explicity should be implicit. Vim allow `g:` but it is not recommended.
        # SEE: https://github.com/Kuniwak/vint/pull/136
        return ScopeVisibilityHint(
            ScopeVisibility.GLOBAL_LIKE,
            ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED
        )

    if not context_scope:
        # We can not detect implicit scope visibility if context scope is not
        # specified.
        return ScopeVisibilityHint(
            ScopeVisibility.UNANALYZABLE,
            ExplicityOfScopeVisibility.UNANALYZABLE
        )

    current_scope_visibility = context_scope.scope_visibility

    # A lambda argument declaration or the references can not have any explicit scope prefix.
    if current_scope_visibility is ScopeVisibility.LAMBDA:
        if is_lambda_argument_identifier(id_node):
            # It can not have any explicit scope prefix.
            explicity = ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED
        else:
            # We can not detect the scope of an implicit variable until
            # we know whether the variable can reach to a lambda argument or not.
            # If it can reach to a lambda argument, then it is IMPLICIT_BUT_CONSTRAINED otherwise IMPLICIT.
            explicity = ExplicityOfScopeVisibility.IMPLICIT_OR_LAMBDA
    else:
        explicity = ExplicityOfScopeVisibility.IMPLICIT

    if current_scope_visibility is ScopeVisibility.SCRIPT_LOCAL:
        # Implicit scope variable will be resolved as a global variable when
        # current scope is script local.
        return ScopeVisibilityHint(
            ScopeVisibility.GLOBAL_LIKE,
            explicity
        )

    # Otherwise be a function local variable.
    return ScopeVisibilityHint(
        ScopeVisibility.FUNCTION_LOCAL,
        explicity
    )


def _get_explicit_scope_visibility(id_node): # type: (Dict[str, Any]) -> Optional[ScopeVisibility]
    # See :help internal-variables
    scope_prefix = id_node['value'][0:2]

    if is_function_identifier(id_node) and is_declarative_identifier(id_node):
        return FunctionDeclarationIdentifierScopePrefixToScopeVisibility.get(scope_prefix)
    else:
        return VariableIdentifierScopePrefixToScopeVisibility.get(scope_prefix)


def _is_just_global(id_node): # type: (Dict[str, Any]) -> bool
    # See :help internal-variables
    return id_node['value'][0:2] == 'g:'
