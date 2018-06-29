from typing import Dict, Any, Optional
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.scope import (
    ScopeVisibility,
    ExplicityOfScopeVisibility,
)
from vint.ast.plugin.scope_plugin.scope_detector import (
    is_analyzable_identifier,
    IdentifierLikeNodeTypes,
)
from vint.ast.plugin.scope_plugin.reference_reachability_tester import ReferenceReachabilityTester


ImplicitScopeVisibilityToIdentifierScopePrefix = {
    ScopeVisibility.GLOBAL_LIKE: 'g:',
    ScopeVisibility.FUNCTION_LOCAL: 'l:',
    ScopeVisibility.BUILTIN: 'v:',
}


def normalize_variable_name(node, reachability_tester):
    # type: (Dict[str, Any], ReferenceReachabilityTester) -> Optional[str]
    """ Returns normalized variable name.
    Normalizing means that variable names get explicit visibility by
    visibility prefix such as: "g:", "s:", ...

    Returns None if the specified node is unanalyzable.
    A node is unanalyzable if:

    - the node is not identifier-like
    - the node is named dynamically
    """

    node_type = NodeType(node['type'])

    if not is_analyzable_identifier(node):
        return None

    if node_type is NodeType.IDENTIFIER:
        return _normalize_identifier_value(node, reachability_tester)

    # Nodes identifier-like without identifier is always normalized because
    # the nodes can not have a visibility prefix.
    if node_type in IdentifierLikeNodeTypes:
        return node['value']


def _normalize_identifier_value(id_node, reachability_tester):
    # type: (Dict[str, Any], ReferenceReachabilityTester) -> str
    visibility_hint = reachability_tester.get_objective_scope_visibility(id_node)
    explicity = visibility_hint.explicity

    # Of course, we can return soon if the variable already have a explicit scope prefix.
    if explicity is ExplicityOfScopeVisibility.EXPLICIT \
            or explicity is ExplicityOfScopeVisibility.UNRECOMMENDED_EXPLICIT:
        return id_node['value']

    # Builtin functions and function arguments can not have any explicit scope prefix.
    if explicity is ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED:
        return id_node['value']

    scope_prefix = ImplicitScopeVisibilityToIdentifierScopePrefix[visibility_hint.scope_visibility]
    return scope_prefix + id_node['value']
