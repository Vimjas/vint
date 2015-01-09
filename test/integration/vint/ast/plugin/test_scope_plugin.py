import unittest
import enum
from pathlib import Path
from pprint import pprint

from vint.ast.parsing import Parser
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin.reference_reachability_tester import (
    is_reference_identifier,
    is_declarative_identifier,
)
from vint.ast.plugin.scope_plugin import ScopePlugin


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')


class Fixtures(enum.Enum):
    REFERENCED_ALL = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_referenced_all_vars.vim')
    REFERENCED_ALL_FUNC = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_referenced_all_funcs.vim')
    REFERENCED_ALL_FUNC_IN_FUNC = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_referenced_all_funcs_in_func.vim')
    REFERENCED_ALL_PARAMS = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_referenced_all_vars_in_func.vim')
    REFERENCED_LOOP_VAR = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_referenced_loop_var.vim')
    UNREFERENCED_PARAMS = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_unreferenced_params.vim')
    UNREFERENCED_FUNC = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_unreferenced_func.vim')
    UNREFERENCED_FUNC_IN_FUNC = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_unreferenced_func_in_func.vim')
    UNREFERENCED_VAR = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_unreferenced_var.vim')
    UNANALYZABLE = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_unanalyzable_variables.vim')


class TestScopePlugin(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path.value)
        return ast


    def assertVariablesUnused(self, expected_variables_unused, scope_plugin, ast):
        dec_id_footstamp_map = {id_name: False for id_name
                                in expected_variables_unused.values()}

        def enter_handler(node):
            if is_declarative_identifier(node):
                id_name = node['value']

                pprint(node)
                self.assertEqual(expected_variables_unused[id_name],
                                 scope_plugin.is_unused_declarative_identifier(node))
                dec_id_footstamp_map[id_name] = True

        traverse(ast, on_enter=enter_handler)

        self.assertTrue(dec_id_footstamp_map.values())


    def assertVariablesUndeclared(self, expected_variables_undeclared, scope_plugin, ast):
        ref_id_footstamp_map = {id_name: False for id_name
                                in expected_variables_undeclared.values()}

        def enter_handler(node):
            if is_reference_identifier(node):
                id_name = node['value']

                pprint(node)
                self.assertEqual(expected_variables_undeclared[id_name],
                                 scope_plugin.is_unreachable_reference_identifier(node))
                ref_id_footstamp_map[id_name] = True

        traverse(ast, on_enter=enter_handler)

        # Check all exlected identifiers were tested
        self.assertTrue(ref_id_footstamp_map.values())


    def test_reference_reachability_with_referenced_all(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            'g:explicit_global_var': False,
            'b:buffer_local_var': False,
            'w:window_local_var': False,
            't:tab_local_var': False,
            's:script_local_var': False,
            'implicit_global_var': False,
            'g:implicit_global_var': False,
            '$ENV_VAR': False,
            '@"': False,
            '&opt_var': False,
            'v:count': False,
            'count': False,
            'g:': False,
            'b:': False,
            'w:': False,
            't:': False,
            'v:': False,
            'v:key': False,
            'v:val': False,
            'filter': False,
            'g:dict': True,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_reference_reachability_with_referenced_all_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            'g:ExplicitGlobalFunc': False,
            's:ScriptLocalFunc': False,
            'ImplicitGlobalFunc': False,
            'g:ImplicitGlobalFunc': False,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_declarative_identifiers_referenced_with_referenced_all_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_unused = {
            'g:ExplicitGlobalFunc': False,
            's:ScriptLocalFunc': False,
            'ImplicitGlobalFunc': False,
        }

        self.assertVariablesUnused(expected_variables_unused,
                                   scope_plugin,
                                   ast)


    def test_reference_reachability_with_referenced_all_funcs_in_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            'g:ExplicitGlobalFunc': False,
            'ImplicitGlobalFunc': False,
            's:ExplicitScriptLocalFunc': False,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_declarative_identifiers_referenced_with_referenced_all_funcs_in_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_unused = {
            'FuncContext': True,
            'g:ExplicitGlobalFunc': False,
            'ImplicitGlobalFunc': False,
            's:ExplicitScriptLocalFunc': False,
        }

        self.assertVariablesUnused(expected_variables_unused,
                                   scope_plugin,
                                   ast)


    def test_declarative_identifiers_referenced_with_referenced_all(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_unused = {
            'g:explicit_global_var': False,
            'b:buffer_local_var': False,
            'w:window_local_var': False,
            't:tab_local_var': False,
            's:script_local_var': False,
            'implicit_global_var': False,
            '$ENV_VAR': False,
            '@"': False,
            '&opt_var': False,
            'v:count': False,
        }

        self.assertVariablesUnused(expected_variables_unused,
                                   scope_plugin,
                                   ast)


    def test_reference_reachability_with_referenced_all_params(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_PARAMS)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_unused = {
            'a:': False,
            'l:': False,
            'a:0': False,
            'a:000': False,

            'a:param': False,

            'a:param1': False,
            'a:param2': False,

            'a:param_var': False,

            'a:param_with_range': False,
            'a:firstline': False,
            'a:lastline': False,
        }

        self.assertVariablesUndeclared(expected_variables_unused,
                                       scope_plugin,
                                       ast)


    def test_reference_reachability_with_referenced_loop_var(self):
        ast = self.create_ast(Fixtures.REFERENCED_LOOP_VAR)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            'g:array': True,
            'g:implicit_global_loop_var': False,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_reference_reachability_with_unreferenced_params(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_PARAMS)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            'param': True,
            'a:1': True,
            'a:firstline': True,
            'a:lastline': True,

            'a:18': True,
            'a:19': True,
            'a:20': True,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_reference_reachability_with_unreferenced_func(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            's:ImplicitGlobalFunc': True,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_declarative_identifiers_referenced_with_unreferenced_func_in_func(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_unused = {
            'FuncContext': True,
            'g:ExplicitGlobalFunc': True,
            'ImplicitGlobalFunc': True,
            's:ExplicitScriptLocalFunc': True,
        }

        self.assertVariablesUnused(expected_variables_unused,
                                   scope_plugin,
                                   ast)


    def test_reference_reachability_with_unreferenced_var(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_VAR)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            's:implicit_global_var': True,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


    def test_reference_reachability_with_unanalyzable(self):
        ast = self.create_ast(Fixtures.UNANALYZABLE)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_variables_undeclared = {
            'list_slice': True,
            'dict': True,
        }

        self.assertVariablesUndeclared(expected_variables_undeclared,
                                       scope_plugin,
                                       ast)


if __name__ == '__main__':
    unittest.main()
