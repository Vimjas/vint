import unittest
from typing import Dict, Any

from vint.ast.plugin.scope_plugin.scope import (
    ScopeVisibility,
    ExplicityOfScopeVisibility,
)
from vint.ast.plugin.scope_plugin.scope_detector import ScopeVisibilityHint
from vint.ast.plugin.scope_plugin.variable_name_normalizer import normalize_variable_name
from vint.ast.plugin.scope_plugin.reference_reachability_tester import ReferenceReachabilityTester

from test.unit.vint.ast.plugin.scope_plugin.stub_node import (
    create_id,
    create_env,
    create_option,
    create_reg,
)

# Shorthand.
Vis = ScopeVisibility
Explicity = ExplicityOfScopeVisibility


class ReferenceReachabilityTesterStub:
    def __init__(self, hint):  # type: (ScopeVisibilityHint) -> None
        self.hint = hint


    def get_objective_scope_visibility(self, _): # type: (Dict[str, Any]) -> ScopeVisibilityHint
        return self.hint



class VariableNameNormalizer(unittest.TestCase):
    def test_parameterized(self):
        test_cases = [
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('g:explicit_global'),
                'g:explicit_global'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('implicit_global'),
                'g:implicit_global'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('implicit_global', is_declarative=False),
                'g:implicit_global'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('l:explicit_function_local'),
                'l:explicit_function_local'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('implicit_function_local'),
                'l:implicit_function_local'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('implicit_function_local', is_declarative=False),
                'l:implicit_function_local'
            ),

            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.UNRECOMMENDED_EXPLICIT
                ),
                create_id('g:ExplicitGlobalFunc', is_function=True),
                'g:ExplicitGlobalFunc'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('s:ExplicitScriptLocalFunc', is_function=True),
                's:ExplicitScriptLocalFunc'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_id('ImplicitGlobalFunc', is_function=True),
                'ImplicitGlobalFunc'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_id('ImplicitGlobalFunc', is_function=True),
                'ImplicitGlobalFunc'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('s:ExplicitScriptLocalFunc', is_function=True),
                's:ExplicitScriptLocalFunc'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_id('ImplicitGlobalFunc', is_declarative=False, is_function=True),
                'ImplicitGlobalFunc'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('l:explicit_function_local'),
                'l:explicit_function_local'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('implicit_function_local'),
                'l:implicit_function_local'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('implicit_function_local', is_declarative=False),
                'l:implicit_function_local'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.FUNCTION_LOCAL,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_id('param', is_declarative=False, is_declarative_parameter=True),
                'param'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.BUILTIN,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('v:count'),
                'v:count'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.BUILTIN,
                    explicity=Explicity.EXPLICIT
                ),
                create_id('v:count'),
                'v:count'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.BUILTIN,
                    explicity=Explicity.IMPLICIT
                ),
                create_id('count'),
                'v:count'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.BUILTIN,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_id('localtime', is_declarative=False, is_function=True),
                'localtime'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_env('$ENV'),
                '$ENV'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_option('&OPT'),
                '&OPT'
            ),
            (
                ScopeVisibilityHint(
                    scope_visibility=Vis.GLOBAL_LIKE,
                    explicity=Explicity.IMPLICIT_BUT_CONSTRAINED
                ),
                create_reg('@"'),
                '@"'
            ),
        ]

        for scope_visibility_hint, node, expected_variable_name in test_cases:
            reachability_tester = ReferenceReachabilityTesterStub(hint=scope_visibility_hint) # type: ReferenceReachabilityTester
            normalized_variable_name = normalize_variable_name(node, reachability_tester)

            self.assertEqual(
                expected_variable_name,
                normalized_variable_name,
                "{name}".format(name=node['value'])
            )


if __name__ == '__main__':
    unittest.main()
