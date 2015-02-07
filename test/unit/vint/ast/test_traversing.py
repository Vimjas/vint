import unittest
import enum
from functools import partial
from test.asserting.ast import get_fixture_path

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType, is_node_type_of
from vint.ast.traversing import traverse, SKIP_CHILDREN, find_all, find_first



class Fixtures(enum.Enum):
    FIND_ALL = get_fixture_path('fixture_traversing_find_all.vim')
    TRAVERSING = get_fixture_path('fixture_to_traverse.vim')


class TestTraverse(unittest.TestCase):
    def create_ast(self, filepath):
        parser = Parser()
        return parser.parse_file(filepath.value)


    def test_traverse(self):
        ast = self.create_ast(Fixtures.TRAVERSING)

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
        traverse(ast,
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
        ast = self.create_ast(Fixtures.TRAVERSING)

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
        traverse(ast,
                 on_enter=on_enter,
                 on_leave=lambda node: actual_order_of_events.append({
                     'node_type': NodeType(node['type']),
                     'handler': 'leave',
                 }))

        self.maxDiff = 2048
        self.assertEqual(actual_order_of_events, expected_order_of_events)


    def test_find_all(self):
        ast = self.create_ast(Fixtures.FIND_ALL)

        found_nodes = find_all(NodeType.ECHO, ast)

        is_let_node = partial(is_node_type_of, NodeType.ECHO)
        are_let_nodes = all(map(is_let_node, found_nodes))

        self.assertEqual(3, len(found_nodes))
        self.assertTrue(are_let_nodes)


    def test_find_with_existent_node_type(self):
        ast = self.create_ast(Fixtures.FIND_ALL)

        found_node = find_first(NodeType.ECHO, ast)

        self.assertTrue(is_node_type_of(NodeType.ECHO, found_node))


    def test_find_with_unexistent_node_type(self):
        ast = self.create_ast(Fixtures.FIND_ALL)

        found_node = find_first(NodeType.WHILE, ast)

        self.assertEqual(found_node, None)


if __name__ == '__main__':
    unittest.main()
