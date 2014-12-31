import unittest
import enum
from pathlib import Path
from pprint import pprint

from vint.ast.parsing import Parser
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin import (
    ScopePlugin,
    REACHABILITY_FLAG,
    REFERECED_FLAG,
)


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


    def assertDeclarativeIdentifiersReferenced(self,
                                               expected_declarative_ids_referenced_map,
                                               ast):
        dec_id_footstamp_map = {id_name: False for id_name
                                in expected_declarative_ids_referenced_map.values()}

        def enter_handler(node):
            if REFERECED_FLAG in node:
                id_name = node['value']

                pprint(node)
                self.assertEqual(expected_declarative_ids_referenced_map[id_name],
                                 node[REFERECED_FLAG])
                dec_id_footstamp_map[id_name] = True

        traverse(ast, on_enter=enter_handler)

        self.assertTrue(dec_id_footstamp_map.values())


    def assertReferencingIdentifiersReachability(self,
                                                 expected_ref_ids_reachability_map,
                                                 ast):
        ref_id_footstamp_map = {id_name: False for id_name
                                in expected_ref_ids_reachability_map.values()}

        def enter_handler(node):
            if REACHABILITY_FLAG in node:
                id_name = node['value']

                pprint(node)
                self.assertEqual(expected_ref_ids_reachability_map[id_name],
                                 node[REACHABILITY_FLAG])
                ref_id_footstamp_map[id_name] = True

        traverse(ast, on_enter=enter_handler)

        # Check all exlected identifiers were tested
        self.assertTrue(ref_id_footstamp_map.values())


    def test_reference_reachability_with_referenced_all(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'g:explicit_global_var': True,
            'b:buffer_local_var': True,
            'w:window_local_var': True,
            't:tab_local_var': True,
            's:script_local_var': True,
            'implicit_global_var': True,
            'g:implicit_global_var': True,
            '$ENV_VAR': True,
            '@"': True,
            '&opt_var': True,
            'v:count': True,
            'count': True,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_reference_reachability_with_referenced_all_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'g:ExplicitGlobalFunc': True,
            'b:BufferLocalFunc': True,
            'w:WindowLocalFunc': True,
            't:TabLocalFunc': True,
            's:ScriptLocalFunc': True,
            'ImplicitGlobalFunc': True,
            'g:ImplicitGlobalFunc': True,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_declarative_identifiers_referenced_with_referenced_all_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_declarative_ids_referenced_map = {
            'g:ExplicitGlobalFunc': True,
            'b:BufferLocalFunc': True,
            'w:WindowLocalFunc': True,
            't:TabLocalFunc': True,
            's:ScriptLocalFunc': True,
            'ImplicitGlobalFunc': True,
        }

        self.assertDeclarativeIdentifiersReferenced(expected_declarative_ids_referenced_map,
                                                    ast)


    def test_reference_reachability_with_referenced_all_funcs_in_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'l:ExplicitFuncLocalFunc': True,
            'ExplicitFuncLocalFunc': True,

            'l:ImplicitFuncLocalFunc': True,
            'ImplicitFuncLocalFunc': True,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_declarative_identifiers_referenced_with_referenced_all_funcs_in_func(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_declarative_ids_referenced_map = {
            'FuncContext': False,
            'l:ExplicitFuncLocalFunc': True,
            'ImplicitFuncLocalFunc': True,
        }

        self.assertDeclarativeIdentifiersReferenced(expected_declarative_ids_referenced_map,
                                                    ast)


    def test_declarative_identifiers_referenced_with_referenced_all(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_declarative_ids_referenced_map = {
            'g:explicit_global_var': True,
            'b:buffer_local_var': True,
            'w:window_local_var': True,
            't:tab_local_var': True,
            's:script_local_var': True,
            'implicit_global_var': True,
            '$ENV_VAR': True,
            '@"': True,
            '&opt_var': True,
            'v:count': True,
        }

        self.assertDeclarativeIdentifiersReferenced(expected_declarative_ids_referenced_map,
                                                    ast)


    def test_reference_reachability_with_referenced_all_params(self):
        ast = self.create_ast(Fixtures.REFERENCED_ALL_PARAMS)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_declarative_ids_referenced_map = {
            'a:0': True,
            'a:000': True,

            'a:param': True,

            'a:param1': True,
            'a:param2': True,

            'a:param_var': True,

            'a:param_with_range': True,
            'a:firstline': True,
            'a:lastline': True,
        }

        self.assertReferencingIdentifiersReachability(expected_declarative_ids_referenced_map,
                                                      ast)


    def test_reference_reachability_with_referenced_loop_var(self):
        ast = self.create_ast(Fixtures.REFERENCED_LOOP_VAR)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'g:array': False,
            'g:implicit_global_loop_var': True,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_reference_reachability_with_unreferenced_params(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_PARAMS)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'param': False,
            'a:1': False,
            'a:firstline': False,
            'a:lastline': False,

            'a:18': False,
            'a:19': False,
            'a:20': False,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_reference_reachability_with_unreferenced_func(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            's:ImplicitGlobalFunc': False,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_reference_reachability_with_unreferenced_func_in_func(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'l:ExplicitFuncLocalFunc': False,
            'ExplicitFuncLocalFunc': False,
            'l:ImplicitFuncLocalFunc': False,
            'ImplicitFuncLocalFunc': False,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_declarative_identifiers_referenced_with_unreferenced_func_in_func(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_FUNC_IN_FUNC)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_declarative_ids_referenced_map = {
            'FuncContext': False,
            'l:ExplicitFuncLocalFunc': False,
            'ImplicitFuncLocalFunc': False,
        }

        self.assertDeclarativeIdentifiersReferenced(expected_declarative_ids_referenced_map,
                                                    ast)


    def test_reference_reachability_with_unreferenced_var(self):
        ast = self.create_ast(Fixtures.UNREFERENCED_VAR)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            's:implicit_global_var': False,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


    def test_reference_reachability_with_unanalyzable(self):
        ast = self.create_ast(Fixtures.UNANALYZABLE)

        scope_plugin = ScopePlugin()
        scope_plugin.process(ast)

        expected_ref_ids_reachability_map = {
            'list_slice': False,
            'dict': False,
        }

        self.assertReferencingIdentifiersReachability(expected_ref_ids_reachability_map,
                                                      ast)


if __name__ == '__main__':
    unittest.main()
