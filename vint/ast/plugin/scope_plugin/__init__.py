from vint.ast.plugin.abstract_ast_plugin import AbstractASTPlugin
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
    detect_possible_scope_visibility as _detect_possible_scope_visibility,
)
from vint.ast.plugin.scope_plugin.identifier_attribute import (
    is_autoload_identifier as _is_autoload_identifier,
    is_function_identifier as _is_function_identifier,
)
from vint.ast.plugin.scope_plugin.variable_name_normalizer import (
    normalize_variable_name as _normalize_variable_name
)


# Expose to out of ScopePlugin
ScopeVisibility = _ScopeVisibility
ExplicityOfScopeVisibility = _ExplicityOfScopeVisibility


class ScopePlugin(AbstractASTPlugin):
    def __init__(self):
        super(ScopePlugin, self).__init__()
        self._ref_tester = ReferenceReachabilityTester()


    def process(self, ast):
        processed_ast = self._ref_tester.process(ast)
        return processed_ast


    def _get_link_registry(self):
        # NOTE: This is a hack for performance. We should build LinkRegistry
        # by this method if ReferenceReachabilityTester hide the link_registry.
        return self._ref_tester._scope_linker.link_registry


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
        scope_visibility_hint = self._ref_tester.get_objective_scope_visibility(node)
        return scope_visibility_hint.scope_visibility


    def get_explicity_of_scope_visibility(self, node):
        scope_visibility_hint = self._ref_tester.get_objective_scope_visibility(node)
        return scope_visibility_hint.explicity


    def normalize_variable_name(self, node):
        return _normalize_variable_name(node, self._ref_tester)
