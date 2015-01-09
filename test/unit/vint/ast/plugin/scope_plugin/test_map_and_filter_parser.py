import unittest
from pathlib import Path
import enum

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin.map_and_filter_parser import (
    MapAndFilterParser,
    get_string_expr_content,
)


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')



class Fixtures(enum.Enum):
    MAP_AND_FILTER_VARIABLE = Path(FIXTURE_BASE_PATH,
                                   'fixture_to_scope_plugin_map_and_filter.vim')


class TestMapAndFilterParser(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path.value)
        return ast


    def test_process_with_map_function(self):
        ast = self.create_ast(Fixtures.MAP_AND_FILTER_VARIABLE)
        parser = MapAndFilterParser()
        got_ast = parser.process(ast)

        string_expr_nodes = get_string_expr_content(got_ast['body'][0]['left'])
        self.assertEqual('v:val', string_expr_nodes[0]['left'].get('value'))


    def test_process_with_filter_function(self):
        ast = self.create_ast(Fixtures.MAP_AND_FILTER_VARIABLE)
        parser = MapAndFilterParser()
        got_ast = parser.process(ast)

        string_expr_nodes = get_string_expr_content(got_ast['body'][1]['left'])
        self.assertEqual('v:key', string_expr_nodes[0]['left'].get('value'))


    def test_traverse(self):
        ast = self.create_ast(Fixtures.MAP_AND_FILTER_VARIABLE)
        parser = MapAndFilterParser()
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



if __name__ == '__main__':
    unittest.main()
