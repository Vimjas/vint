import unittest
from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from test.asserting.ast import get_fixture_path

FIXTURE_FILE = get_fixture_path('fixture_to_parse.vim')
FIXTURE_FILE_FF_DOF_FENC_CP932 = get_fixture_path('fixture_to_parse_windows.vim')


class TestParser(unittest.TestCase):
    def test_parse_file(self):
        parser = Parser()
        ast = parser.parse_file(FIXTURE_FILE)
        self.assertIs(ast['type'], 1)


    def test_parse_file_on_ff_dos_and_fenc_cp932(self):
        parser = Parser()
        ast = parser.parse_file(FIXTURE_FILE_FF_DOF_FENC_CP932)
        self.assertIs(ast['type'], 1)


    def test_parse_redir_with_identifier(self):
        parser = Parser()
        redir_cmd_node = {
            'type': NodeType.EXCMD.value,
            'ea': {
                'argpos': {'col': 6, 'i': 5, 'lnum': 1},
            },
            'str': 'redir=>redir',
        }
        ast = parser.parse_redir(redir_cmd_node)

        expected_pos = {
            'col': 8,
            'i': 7,
            'lnum': 1,
        }
        expected_node_type = NodeType.IDENTIFIER

        self.assertEqual(expected_node_type, NodeType(ast['type']))
        self.assertEqual(expected_pos, ast['pos'])


    def test_parse_redir_with_dot(self):
        parser = Parser()
        redir_cmd_node = {
            'type': NodeType.EXCMD.value,
            'ea': {
                'argpos': {'col': 7, 'i': 6, 'lnum': 1},
            },
            'str': 'redir => s:dict.redir',
        }
        ast = parser.parse_redir(redir_cmd_node)

        expected_pos = {
            'col': 16,
            'i': 15,
            'lnum': 1,
        }
        expected_node_type = NodeType.DOT

        self.assertEqual(expected_node_type, NodeType(ast['type']))
        self.assertEqual(expected_pos, ast['pos'])


if __name__ == '__main__':
    unittest.main()
