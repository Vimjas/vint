import unittest
from vint.ast.node_type import NodeType


class TestNodeType(unittest.TestCase):
    def test_get_node_type_name(self):
        self.assertIs(NodeType(1), NodeType.TOPLEVEL)
        self.assertIs(NodeType(89), NodeType.REG)

if __name__ == '__main__':
    unittest.main()
