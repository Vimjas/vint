import unittest
from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from test.asserting.ast import get_fixture_path

FIXTURE_FILE = get_fixture_path('fixture_to_parse.vim')
FIXTURE_FILE_EMPTY = get_fixture_path('fixture_to_parse_empty_file.vim')
FIXTURE_FILE_FF_DOS_FENC_CP932 = get_fixture_path('fixture_to_parse_windows.vim')
FIXTURE_FILE_NEOVIM = get_fixture_path('fixture_to_parse_neovim.vim')


class TestParser(unittest.TestCase):
    def test_parse_file(self):
        parser = Parser()
        ast = parser.parse_file(FIXTURE_FILE)
        self.assertIs(ast['type'], 1)


    def test_parse_file_on_ff_dos_and_fenc_cp932(self):
        parser = Parser()
        ast = parser.parse_file(FIXTURE_FILE_FF_DOS_FENC_CP932)
        self.assertIs(ast['type'], 1)


    def test_parse_file_when_neovim_enabled(self):
        parser = Parser(enable_neovim=True)
        ast = parser.parse_file(FIXTURE_FILE_NEOVIM)
        self.assertIs(ast['type'], 1)


    def test_parse_empty_file(self):
        parser = Parser()
        ast = parser.parse_file(FIXTURE_FILE_EMPTY)
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
            'offset': 5
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
            'offset': 11,
        }
        expected_node_type = NodeType.DOT

        self.assertEqual(expected_node_type, NodeType(ast['type']))
        self.assertEqual(expected_pos, ast['pos'])


    def test_parse_string_expr(self):
        parser = Parser()
        redir_cmd_node = {
            'type': NodeType.STRING.value,
            'pos': {'col': 1, 'i': 1, 'lnum': 1},
            'value': '\'v:key ==# "a"\'',
        }
        nodes = parser.parse_string_expr(redir_cmd_node)

        expected_pos = {
            'col': 7,
            'i': 7,
            'lnum': 1,
            'offset': 11,
        }
        expected_node_type = NodeType.EQUALCS

        self.assertEqual(expected_node_type, NodeType(nodes[0]['type']))
        self.assertEqual(expected_pos, nodes[0]['pos'])


if __name__ == '__main__':
    unittest.main()
