import unittest
import enum
from pathlib import Path

from vint.ast.node_type import get_node_type, NodeType
from vint.ast.traversing_handler import traverse_by_handler
from vint.ast.parsing import Parser


FIXTURE_PATH_BASE = Path('test', 'fixture', 'ast')


def get_fixture_path(file_path):
    return Path(FIXTURE_PATH_BASE).joinpath(file_path)


class Fixtures(enum.Enum):
    TRAVERSING = get_fixture_path('fixture_to_traverse.vim')


class TraversingHandlerSpy():
    def __init__(self):
        self.on_enter = {node_type: self._create_logger('on_enter') for node_type in NodeType}
        self.on_leave = {node_type: self._create_logger('on_leave') for node_type in NodeType}
        self.handled_events = []

    def _create_logger(self, event_name):
        def logger(node):
            node_type = get_node_type(node)
            self.handled_events.append((event_name, node_type))

        return logger


class TestTraversingHandler(unittest.TestCase):
    def create_ast(self, filepath):
        parser = Parser()
        return parser.parse_file(filepath.value)

    def test_traverse(self):
        ast = self.create_ast(Fixtures.TRAVERSING)
        spy = TraversingHandlerSpy()

        traverse_by_handler(ast, on_enter=spy.on_enter, on_leave=spy.on_leave)

        expected_order_of_events = [
            ('on_enter', NodeType.TOPLEVEL),
            ('on_enter', NodeType.LET),
            ('on_enter', NodeType.IDENTIFIER),
            ('on_leave', NodeType.IDENTIFIER),
            ('on_enter', NodeType.NUMBER),
            ('on_leave', NodeType.NUMBER),
            ('on_leave', NodeType.LET),
            ('on_enter', NodeType.WHILE),
            ('on_enter', NodeType.SMALLER),
            ('on_enter', NodeType.IDENTIFIER),
            ('on_leave', NodeType.IDENTIFIER),
            ('on_enter', NodeType.NUMBER),
            ('on_leave', NodeType.NUMBER),
            ('on_leave', NodeType.SMALLER),
            ('on_enter', NodeType.ECHO),
            ('on_enter', NodeType.STRING),
            ('on_leave', NodeType.STRING),
            ('on_enter', NodeType.IDENTIFIER),
            ('on_leave', NodeType.IDENTIFIER),
            ('on_leave', NodeType.ECHO),
            ('on_enter', NodeType.LET),
            ('on_enter', NodeType.IDENTIFIER),
            ('on_leave', NodeType.IDENTIFIER),
            ('on_enter', NodeType.NUMBER),
            ('on_leave', NodeType.NUMBER),
            ('on_leave', NodeType.LET),
            ('on_enter', NodeType.ENDWHILE),
            ('on_leave', NodeType.ENDWHILE),
            ('on_leave', NodeType.WHILE),
            ('on_leave', NodeType.TOPLEVEL),
        ]
        self.maxDiff = 2000
        self.assertEqual(spy.handled_events, expected_order_of_events)


if __name__ == '__main__':
    unittest.main()
