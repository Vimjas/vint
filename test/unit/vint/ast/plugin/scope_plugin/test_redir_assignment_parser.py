import unittest
from pathlib import Path
import enum

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin.redir_assignment_parser import (
    RedirAssignmentParser,
    get_redir_content,
)


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')



class Fixtures(enum.Enum):
    REDIR_VARIABLE = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_redir.vim')


class TestRedirAssignmentParser(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path.value)
        return ast


    def test_process(self):
        ast = self.create_ast(Fixtures.REDIR_VARIABLE)
        parser = RedirAssignmentParser()
        got_ast = parser.process(ast)

        got_identifier = get_redir_content(got_ast['body'][0])
        self.assertEqual('g:var', got_identifier.get('value'))


    def test_traverse(self):
        ast = self.create_ast(Fixtures.REDIR_VARIABLE)
        parser = RedirAssignmentParser()
        got_ast = parser.process(ast)

        is_redir_content_visited = {
            'g:var': False,
        }

        def enter_handler(node):
            if NodeType(node['type']) is not NodeType.IDENTIFIER:
                return

            is_redir_content_visited[node['value']] = True

        traverse(got_ast, on_enter=enter_handler)

        self.assertTrue(all(is_redir_content_visited.values()))



if __name__ == '__main__':
    unittest.main()
