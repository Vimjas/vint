import unittest
import lib.parser


class TestParser(unittest.TestCase):
    def test_parse_file(self):
        parser = lib.parser.Parser()
        ast = parser.parse_file('test/fixture/fixture_to_parse.vim')
        self.assertIn('body', ast)

if __name__ == '__main__':
    unittest.main()
