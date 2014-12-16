import unittest
from test.asserting.ast import get_fixture_path

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse, SKIP_CHILDREN

FIXTURE_FILE = get_fixture_path('fixture_to_traverse.vim')


class TestTraverse(unittest.TestCase):
    def setUp(self):
        parser = Parser()
        self.ast = parser.parse_file(FIXTURE_FILE)

    def test_traverse(self):
        expected_order_of_events = [
            {'node_type': NodeType.TOPLEVEL, 'handler': 'enter'},
            {'node_type': NodeType.LET, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'leave'},
            {'node_type': NodeType.NUMBER, 'handler': 'enter'},
            {'node_type': NodeType.NUMBER, 'handler': 'leave'},
            {'node_type': NodeType.LET, 'handler': 'leave'},
            {'node_type': NodeType.WHILE, 'handler': 'enter'},
            {'node_type': NodeType.SMALLER, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'leave'},
            {'node_type': NodeType.NUMBER, 'handler': 'enter'},
            {'node_type': NodeType.NUMBER, 'handler': 'leave'},
            {'node_type': NodeType.SMALLER, 'handler': 'leave'},
            {'node_type': NodeType.ECHO, 'handler': 'enter'},
            {'node_type': NodeType.STRING, 'handler': 'enter'},
            {'node_type': NodeType.STRING, 'handler': 'leave'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'leave'},
            {'node_type': NodeType.ECHO, 'handler': 'leave'},
            {'node_type': NodeType.LET, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'leave'},
            {'node_type': NodeType.NUMBER, 'handler': 'enter'},
            {'node_type': NodeType.NUMBER, 'handler': 'leave'},
            {'node_type': NodeType.LET, 'handler': 'leave'},
            {'node_type': NodeType.ENDWHILE, 'handler': 'enter'},
            {'node_type': NodeType.ENDWHILE, 'handler': 'leave'},
            {'node_type': NodeType.WHILE, 'handler': 'leave'},
            {'node_type': NodeType.TOPLEVEL, 'handler': 'leave'},
        ]

        # Records visit node type name in order
        actual_order_of_events = []
        traverse(self.ast,
                 on_enter=lambda node: actual_order_of_events.append({
                     'node_type': NodeType(node['type']),
                     'handler': 'enter',
                 }),
                 on_leave=lambda node: actual_order_of_events.append({
                     'node_type': NodeType(node['type']),
                     'handler': 'leave',
                 }))

        self.maxDiff = 2048
        self.assertEqual(actual_order_of_events, expected_order_of_events)


    def test_traverse_ignoring_while_children(self):
        expected_order_of_events = [
            {'node_type': NodeType.TOPLEVEL, 'handler': 'enter'},
            {'node_type': NodeType.LET, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'enter'},
            {'node_type': NodeType.IDENTIFIER, 'handler': 'leave'},
            {'node_type': NodeType.NUMBER, 'handler': 'enter'},
            {'node_type': NodeType.NUMBER, 'handler': 'leave'},
            {'node_type': NodeType.LET, 'handler': 'leave'},
            {'node_type': NodeType.WHILE, 'handler': 'enter'},
            {'node_type': NodeType.WHILE, 'handler': 'leave'},
            {'node_type': NodeType.TOPLEVEL, 'handler': 'leave'},
        ]

        def on_enter(node):
            actual_order_of_events.append({
                'node_type': NodeType(node['type']),
                'handler': 'enter',
            })

            if NodeType(node['type']) is NodeType.WHILE:
                return SKIP_CHILDREN


        # Records visit node type name in order
        actual_order_of_events = []
        traverse(self.ast,
                 on_enter=on_enter,
                 on_leave=lambda node: actual_order_of_events.append({
                     'node_type': NodeType(node['type']),
                     'handler': 'leave',
                 }))

        self.maxDiff = 2048
        self.assertEqual(actual_order_of_events, expected_order_of_events)


if __name__ == '__main__':
    unittest.main()
