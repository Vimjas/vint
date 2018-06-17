import unittest
from pathlib import Path
import enum

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin.call_node_parser import (
    CallNodeParser,
    get_lambda_string_expr_content,
    FUNCTION_REFERENCE_STRING_EXPR_CONTENT,
)


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')



class Fixtures(enum.Enum):
    MAP_AND_FILTER_VARIABLE = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_map_and_filter.vim')
    ISSUE_256 = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_issue_256.vim')
    NESTED = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_nested_map_and_filter.vim')
    ISSUE_274_CALL = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_issue_274_call.vim')
    ISSUE_274_FUNCTION = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_issue_274_function.vim')


class TestCallNodeParser(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path.value)
        return ast


    def test_process_with_map_function(self):
        ast = self.create_ast(Fixtures.MAP_AND_FILTER_VARIABLE)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        string_expr_nodes = get_lambda_string_expr_content(got_ast['body'][0]['left']['rlist'][1])
        self.assertEqual('v:val', string_expr_nodes[0]['left'].get('value'))


    def test_process_with_filter_function(self):
        ast = self.create_ast(Fixtures.MAP_AND_FILTER_VARIABLE)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        string_expr_nodes = get_lambda_string_expr_content(got_ast['body'][1]['left']['rlist'][1])
        self.assertEqual('v:key', string_expr_nodes[0]['left'].get('value'))


    def test_traverse(self):
        ast = self.create_ast(Fixtures.MAP_AND_FILTER_VARIABLE)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        is_map_and_filter_content_visited = {
            'v:val': False,
            'v:key': False,
        }

        def enter_handler(node):
            if NodeType(node['type']) is not NodeType.IDENTIFIER:
                return

            is_map_and_filter_content_visited[node['value']] = True

        traverse(got_ast, on_enter=enter_handler)

        self.assertTrue(all(is_map_and_filter_content_visited.values()))


    def test_issue_256(self):
        ast = self.create_ast(Fixtures.ISSUE_256)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        self.assertIsNotNone(got_ast)


    def test_nested_map(self):
        ast = self.create_ast(Fixtures.NESTED)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        nested_map_ast = get_lambda_string_expr_content(got_ast['body'][0]['left'])[0]
        self.assertIsNotNone(get_lambda_string_expr_content(nested_map_ast))


    def test_nested_filter(self):
        ast = self.create_ast(Fixtures.NESTED)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        nested_filter_ast = get_lambda_string_expr_content(got_ast['body'][1]['left'])[0]
        self.assertIsNotNone(get_lambda_string_expr_content(nested_filter_ast))


    def test_issue_274_call(self):
        ast = self.create_ast(Fixtures.ISSUE_274_CALL)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        call_node = got_ast['body'][0]['left']['rlist'][0]
        self.assertTrue(FUNCTION_REFERENCE_STRING_EXPR_CONTENT in call_node)
        self.assertEqual(len(call_node[FUNCTION_REFERENCE_STRING_EXPR_CONTENT]), 1)


    def test_issue_274_function(self):
        ast = self.create_ast(Fixtures.ISSUE_274_FUNCTION)
        parser = CallNodeParser()
        got_ast = parser.process(ast)

        call_node = got_ast['body'][0]['left']['rlist'][0]
        self.assertTrue(FUNCTION_REFERENCE_STRING_EXPR_CONTENT in call_node)
        self.assertEqual(len(call_node[FUNCTION_REFERENCE_STRING_EXPR_CONTENT]), 1)


if __name__ == '__main__':
    unittest.main()
