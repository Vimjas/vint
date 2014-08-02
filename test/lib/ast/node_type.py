import unittest
import lib.ast.node_type


class TestNodeType(unittest.TestCase):
    def test_get_node_type_name(self):
        get_node_type_name = lib.ast.node_type.get_node_type_name

        self.assertIs(get_node_type_name(1), 'TOPLEVEL')
        self.assertIs(get_node_type_name(89), 'REG')

if __name__ == '__main__':
    unittest.main()
