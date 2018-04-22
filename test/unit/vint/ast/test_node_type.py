import unittest
from vint.ast.node_type import NodeType, get_node_type, is_node_type_of


class TestNodeType(unittest.TestCase):
    def test_get_node_type_name(self):
        self.assertIs(NodeType(1), NodeType.TOPLEVEL)
        self.assertIs(NodeType(89), NodeType.REG)


    def test_get_node_type(self):
        node_stub = {'type': NodeType.TOPLEVEL.value}

        self.assertEqual(get_node_type(node_stub), NodeType.TOPLEVEL)


    def test_is_node_type_of(self):
        node_stub = {'type': NodeType.TOPLEVEL.value}

        self.assertTrue(is_node_type_of(NodeType.TOPLEVEL, node_stub))
        self.assertFalse(is_node_type_of(NodeType.ECHO, node_stub))


if __name__ == '__main__':
    unittest.main()
