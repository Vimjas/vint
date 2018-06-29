from typing import Dict, List, Any, Optional
import enum


class VariableDeclaration:
    def __init__(self, explicity, is_builtin, is_explicit_lambda_argument):
        # type: (str, ExplicityOfScopeVisibility, bool, bool) -> None
        self.explicity = explicity
        self.is_builtin = is_builtin

        # NOTE: This property used for determining whether the implicit variable is constrained by lambda or not.
        self.is_explicit_lambda_argument = is_explicit_lambda_argument


class GlobalVariableDeclaration:
    """ An alternate value of variable declarations. It means the variable is defined on global like scope,
    but it can not be a concrete VariableDeclaration because Vint can not know whether it is defined as well.
    """
    pass


GLOBAL_VARIABLE_DECLARATION = GlobalVariableDeclaration()


class Scope:
    def __init__(self, scope_visibility):
        # type: (ScopeVisibility) -> None
        self.scope_visibility = scope_visibility
        self.functions = {}  # type: Dict[str, List[VariableDeclaration]]
        self.variables = {}  # type: Dict[str, List[VariableDeclaration]]
        self.child_scopes = []  # type: List[Scope]

        # XXX: self.parent is typed as Optional[Scope], so it can be None. But the None has 2 meanings:
        #   - Parent scope is not attached yet
        #   - This scope is root scope
        # But it makes debugging hard, so self.parent is a debug value until the self.parent is set by other.
        self.parent = 'not attached yet' # type: Optional[Scope]


@enum.unique
class ScopeVisibility(enum.Enum):
    """ 6 types scope visibility.
    We interest to analyze the variable scope by checking a single file.
    So, we do not interest to the strict visibility of the scopes that have a
    larger visibility than script local.
    """
    GLOBAL_LIKE = 0
    BUILTIN = 1
    SCRIPT_LOCAL = 2
    FUNCTION_LOCAL = 3
    UNANALYZABLE = 4
    INVALID = 5
    LAMBDA = 6


@enum.unique
class ExplicityOfScopeVisibility(enum.Enum):
    EXPLICIT = 0
    IMPLICIT = 1
    IMPLICIT_OR_LAMBDA = 2
    # It means implicit but the variable can not have explicit scope prefix.
    # For example, function arguments and builtin functions can not have explicit scope prefix.
    IMPLICIT_BUT_CONSTRAINED = 3
    UNANALYZABLE = 4

    # SEE: https://github.com/Kuniwak/vint/pull/136
    UNRECOMMENDED_EXPLICIT=5
