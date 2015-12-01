from vint.ast.plugin.scope_plugin.reference_reachability_tester import (
    ReferenceReachabilityTester,
    is_reference_identifier as _is_reference_identifier,
    is_declarative_identifier as _is_declarative_identifier,
    is_reachable_reference_identifier as _is_reachable_reference_identifier,
    is_referenced_declarative_identifier as _is_referenced_declarative_identifier,
)
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeVisibility as _ScopeVisibility,
    ExplicityOfScopeVisibility as _ExplicityOfScopeVisibility,
    detect_scope_visibility as _detect_scope_visibility,
    get_explicity_of_scope_visibility as _get_explicity_of_scope_visibility,
    normalize_variable_name as _normalize_variable_name,
)
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    is_autoload_identifier as _is_autoload_identifier,
    is_function_identifier as _is_function_identifier,
)


# Expose to out of ScopePlugin
ScopeVisibility = _ScopeVisibility
ExplicityOfScopeVisibility = _ExplicityOfScopeVisibility


class ScopePlugin(object):
    def __init__(self):
        self._ref_tester = ReferenceReachabilityTester()


    def process(self, ast):
        processed_ast = self._ref_tester.process(ast)
        return processed_ast


    def _get_link_registry(self):
        # NOTE: This is a hack for performance. We should build LinkRegistry
        # by this method if ReferenceReachabilityTester hide the link_registry.
        return self._ref_tester._link_registry


    def is_unreachable_reference_identifier(self, node):
        return _is_reference_identifier(node) \
            and not _is_reachable_reference_identifier(node)


    def is_unused_declarative_identifier(self, node):
        return _is_declarative_identifier(node) \
            and not _is_referenced_declarative_identifier(node)


    def is_autoload_identifier(self, node):
        return _is_autoload_identifier(node)


    def is_function_identifier(self, node):
        return _is_function_identifier(node)

    def get_objective_scope_visibility(self, node):
        link_registry = self._get_link_registry()
        context_scope = link_registry.get_context_scope_by_identifier(node)
        scope_visibility_hint = _detect_scope_visibility(node, context_scope)
        return scope_visibility_hint['scope_visibility']


    def get_explicity_of_scope_visibility(self, node):
        return _get_explicity_of_scope_visibility(node)


    def normalize_variable_name(self, node):
        link_registry = self._get_link_registry()
        context_scope = link_registry.get_context_scope_by_identifier(node)
        return _normalize_variable_name(node, context_scope)
