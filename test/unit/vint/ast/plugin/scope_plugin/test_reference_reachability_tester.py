import unittest
from pathlib import Path
import enum

from vint.ast.parsing import Parser
from vint.ast.plugin.scope_plugin.reference_reachability_tester import (
    ReferenceReachabilityTester,
    is_reachable_reference_identifier,
    is_referenced_declarative_identifier,
)


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')



class Fixtures(enum.Enum):
    DECLARING_AND_REFERENCING = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_and_referencing.vim')
    MISS_DECLARATION = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_missing_declaration.vim')
    SAME_NAME_FUNCTION_AND_REFERENCE = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_same_name_function_and_variable.vim')
    FUNCTION_REF = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_function_ref.vim')
    BUILTIN = Path(
        FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_using_builtin.vim')



class TestReferenceReachabilityTester(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path.value)
        return ast


    def test_reachable_reference_by_process(self):
        ast = self.create_ast(Fixtures.DECLARING_AND_REFERENCING)

        ref_id_node = ast['body'][1]['left']['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertTrue(is_reachable_reference_identifier(ref_id_node))


    def test_referenced_variable_by_process(self):
        ast = self.create_ast(Fixtures.DECLARING_AND_REFERENCING)

        declarative_id_node = ast['body'][0]['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertTrue(is_referenced_declarative_identifier(declarative_id_node))


    def test_unreachable_reference_by_process(self):
        ast = self.create_ast(Fixtures.MISS_DECLARATION)

        ref_id_node = ast['body'][1]['left']['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertFalse(is_reachable_reference_identifier(ref_id_node))


    def test_unreferenced_reference_by_process(self):
        ast = self.create_ast(Fixtures.MISS_DECLARATION)

        declarative_id_node = ast['body'][0]['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertFalse(is_referenced_declarative_identifier(declarative_id_node))


    def test_referenced_variable_reference_by_process(self):
        ast = self.create_ast(Fixtures.SAME_NAME_FUNCTION_AND_REFERENCE)

        declarative_variable_node = ast['body'][0]['left']
        declarative_function_node = ast['body'][1]['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertTrue(is_referenced_declarative_identifier(declarative_variable_node))
        self.assertFalse(is_referenced_declarative_identifier(declarative_function_node))


    def test_referenced_function_reference_by_process(self):
        ast = self.create_ast(Fixtures.FUNCTION_REF)

        declarative_variable_node = ast['body'][0]['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertTrue(is_referenced_declarative_identifier(declarative_variable_node))


    def test_builtin_reference_by_process(self):
        ast = self.create_ast(Fixtures.BUILTIN)

        ref_id_node = ast['body'][0]['left']['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertTrue(is_reachable_reference_identifier(ref_id_node))


if __name__ == '__main__':
    unittest.main()
