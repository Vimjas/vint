import unittest
from vint.ast.plugin.scope_plugin.scope import Scope, ScopeVisibility, ExplicityOfScopeVisibility
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeVisibilityHint,
    detect_possible_scope_visibility,
)
from test.unit.vint.ast.plugin.scope_plugin.stub_node import (
    create_id,
    create_curlyname,
    create_subscript_member,
)

# Shorthand
Vis = ScopeVisibility
Explicity = ExplicityOfScopeVisibility


def create_scope(visibility):  # type: (ScopeVisibility) -> Scope
    return Scope(scope_visibility=visibility)


def create_scope_visibility_hint(visibility, explicity=ExplicityOfScopeVisibility.EXPLICIT):
    return ScopeVisibilityHint(
        scope_visibility=visibility,
        explicity=explicity,
    )


class TestScopeDetector(unittest.TestCase):
    def test_parameterized(self):
        test_cases = [
            # Declarative variable test
            (Vis.SCRIPT_LOCAL, create_id('g:explicit_global'), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('implicit_global'), Vis.GLOBAL_LIKE, Explicity.IMPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('g:explicit_global'), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('b:buffer_local'), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('b:buffer_local'), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('w:window_local'), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('w:window_local'), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('s:script_local'), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('s:script_local'), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),

            (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local'), Vis.FUNCTION_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('implicit_function_local'), Vis.FUNCTION_LOCAL, Explicity.IMPLICIT),

            (Vis.FUNCTION_LOCAL, create_id('param', is_declarative=True, is_declarative_parameter=True), Vis.FUNCTION_LOCAL, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.SCRIPT_LOCAL, create_id('v:count'), Vis.BUILTIN, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('v:count'), Vis.BUILTIN, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('count'), Vis.BUILTIN, Explicity.IMPLICIT),

            (Vis.SCRIPT_LOCAL, create_curlyname(), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),
            (Vis.FUNCTION_LOCAL, create_curlyname(), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),

            (Vis.SCRIPT_LOCAL, create_subscript_member(), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),
            (Vis.FUNCTION_LOCAL, create_subscript_member(), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),

            (Vis.SCRIPT_LOCAL, create_id('g:ExplicitGlobalFunc', is_function=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('ImplicitGlobalFunc', is_function=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.SCRIPT_LOCAL, create_id('g:file#explicit_global_func', is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('file#implicit_global_func', is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.FUNCTION_LOCAL, create_id('g:ExplicitGlobalFunc', is_function=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('ImplicitGlobalFunc', is_function=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.FUNCTION_LOCAL, create_id('g:file#explicit_global_func', is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('file#implicit_global_func', is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.SCRIPT_LOCAL, create_id('s:ScriptLocalFunc', is_function=True), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('s:ScriptLocalFunc', is_function=True), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('t:InvalidScopeFunc', is_function=True), Vis.INVALID, Explicity.EXPLICIT),

            # Referencing variable test
            (Vis.SCRIPT_LOCAL, create_id('g:explicit_global', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('implicit_global', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.IMPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('g:explicit_global', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('b:buffer_local', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('b:buffer_local', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('w:window_local', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('w:window_local', is_declarative=False), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('s:script_local', is_declarative=False), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('s:script_local', is_declarative=False), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),

            (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local', is_declarative=False), Vis.FUNCTION_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('implicit_function_local', is_declarative=False), Vis.FUNCTION_LOCAL, Explicity.IMPLICIT),

            (Vis.FUNCTION_LOCAL, create_id('a:param', is_declarative=False), Vis.FUNCTION_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('a:000', is_declarative=False), Vis.FUNCTION_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('a:1', is_declarative=False), Vis.FUNCTION_LOCAL, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('v:count', is_declarative=False), Vis.BUILTIN, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('v:count', is_declarative=False), Vis.BUILTIN, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('count', is_declarative=False), Vis.BUILTIN, Explicity.IMPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('localtime', is_declarative=False, is_function=True), Vis.BUILTIN, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.SCRIPT_LOCAL, create_curlyname(is_declarative=False), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),
            (Vis.FUNCTION_LOCAL, create_curlyname(is_declarative=False), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),

            (Vis.SCRIPT_LOCAL, create_subscript_member(is_declarative=False), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),
            (Vis.FUNCTION_LOCAL, create_subscript_member(is_declarative=False), Vis.UNANALYZABLE, Explicity.UNANALYZABLE),

            (Vis.SCRIPT_LOCAL, create_id('g:ExplicitGlobalFunc', is_declarative=False, is_function=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('ImplicitGlobalFunc', is_declarative=False, is_function=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.SCRIPT_LOCAL, create_id('g:file#explicit_global_func', is_declarative=False, is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.SCRIPT_LOCAL, create_id('file#implicit_global_func', is_declarative=False, is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.FUNCTION_LOCAL, create_id('g:ExplicitGlobalFunc', is_declarative=False, is_function=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('ImplicitGlobalFunc', is_declarative=False, is_function=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.FUNCTION_LOCAL, create_id('g:file#explicit_global_func', is_declarative=False, is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.UNRECOMMENDED_EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('file#implicit_global_func', is_declarative=False, is_function=True, is_autoload=True), Vis.GLOBAL_LIKE, Explicity.IMPLICIT_BUT_CONSTRAINED),

            (Vis.SCRIPT_LOCAL, create_id('s:ScriptLocalFunc', is_declarative=False, is_function=True), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),
            (Vis.FUNCTION_LOCAL, create_id('s:ScriptLocalFunc', is_declarative=False, is_function=True), Vis.SCRIPT_LOCAL, Explicity.EXPLICIT),

            (Vis.SCRIPT_LOCAL, create_id('t:TabLocalFuncRef', is_declarative=False, is_function=True), Vis.GLOBAL_LIKE, Explicity.EXPLICIT),
        ]

        for context_scope_visibility, id_node, expected_scope_visibility, expected_explicity in test_cases:
            scope = create_scope(context_scope_visibility)
            scope_visibility_hint = detect_possible_scope_visibility(id_node, scope)

            self.assertEqual(expected_scope_visibility, scope_visibility_hint.scope_visibility, id_node)
            self.assertEqual(expected_explicity, scope_visibility_hint.explicity, id_node)


if __name__ == '__main__':
    unittest.main()
