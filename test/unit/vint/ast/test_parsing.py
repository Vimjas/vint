import unittest
from vint.ast.parsing import Parser
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


if __name__ == '__main__':
    unittest.main()
