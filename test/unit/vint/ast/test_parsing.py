import unittest
from vint.ast.parsing import Parser
from test.asserting.ast import get_fixture_path

FIXTURE_FILE = get_fixture_path('fixture_to_parse.vim')


class TestParser(unittest.TestCase):
    def test_parse_file(self):
        parser = Parser()
        ast = parser.parse_file(FIXTURE_FILE)
        self.assertIs(ast['type'], 1)


if __name__ == '__main__':
    unittest.main()
