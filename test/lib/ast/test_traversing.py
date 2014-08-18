import unittest
from test.asserting.ast import get_fixture_path

from lib.ast.parsing import Parser
from lib.ast.nodetype import NodeType
from lib.ast.traversing import traverse

FIXTURE_FILE = get_fixture_path('fixture_to_traverse.vim')


class TestTraverse(unittest.TestCase):
    def setUp(self):
        parser = Parser()
        self.ast = parser.parse_file(FIXTURE_FILE)

    def test_traverse(self):
        expected_order_of_visit = [
            NodeType.TOPLEVEL,
            NodeType.LET,
            NodeType.IDENTIFIER,
            NodeType.NUMBER,
            NodeType.WHILE,
            NodeType.ECHO,
            NodeType.STRING,
            NodeType.IDENTIFIER,
            NodeType.LET,
            NodeType.IDENTIFIER,
            NodeType.NUMBER,
            NodeType.SMALLER,
            NodeType.IDENTIFIER,
            NodeType.NUMBER,
            NodeType.ENDWHILE,
        ]

        actual_order_of_visit = []

        # Records visit node type name in order
        record_visit_node_in_order = lambda node: actual_order_of_visit.append(
            NodeType(node['type']))

        traverse(record_visit_node_in_order, self.ast)

        self.assertEqual(actual_order_of_visit, expected_order_of_visit)


if __name__ == '__main__':
    unittest.main()
