import unittest
import lib.ast.parser


class TestParser(unittest.TestCase):
    def test_parse_file(self):
        parser = lib.ast.parser.Parser()
        ast = parser.parse_file('test/fixture/fixture_to_parse.vim')
        self.assertIs(ast['type'], 1)

if __name__ == '__main__':
    unittest.main()
