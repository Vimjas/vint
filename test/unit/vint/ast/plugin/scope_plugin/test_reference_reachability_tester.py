import unittest
from pathlib import Path
import enum

from vint.ast.parsing import Parser
from vint.ast.plugin.scope_plugin.reference_reachability_tester import (
    ReferenceReachabilityTester,
    REACHABILITY_FLAG,
    REFERECED_FLAG,
)


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')



class Fixtures(enum.Enum):
    DECLARING_AND_REFERENCING = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_and_referencing.vim')
    MISS_DECLARATION = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_missing_declaration.vim')



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

        self.assertTrue(ref_id_node[REACHABILITY_FLAG])


    def test_referenced_variable_by_process(self):
        ast = self.create_ast(Fixtures.DECLARING_AND_REFERENCING)

        declarative_id_node = ast['body'][0]['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertTrue(declarative_id_node[REFERECED_FLAG])


    def test_unreachable_reference_by_process(self):
        ast = self.create_ast(Fixtures.MISS_DECLARATION)

        ref_id_node = ast['body'][1]['left']['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertFalse(ref_id_node[REACHABILITY_FLAG])


    def test_unreferenced_reference_by_process(self):
        ast = self.create_ast(Fixtures.MISS_DECLARATION)

        declarative_id_node = ast['body'][0]['left']

        tester = ReferenceReachabilityTester()
        tester.process(ast)

        self.assertFalse(declarative_id_node[REFERECED_FLAG])


if __name__ == '__main__':
    unittest.main()
