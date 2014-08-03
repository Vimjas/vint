import unittest
from lib.ast.nodetype import get_node_type_name


class TestNodeType(unittest.TestCase):
    def test_get_node_type_name(self):
        self.assertIs(get_node_type_name(1), 'TOPLEVEL')
        self.assertIs(get_node_type_name(89), 'REG')

if __name__ == '__main__':
    unittest.main()
