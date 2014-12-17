import sys
from pprint import pprint
from pathlib import Path

vint_root = Path(__file__).parent.parent
sys.path.append(str(vint_root))

from vint.ast.node_type import NodeType
from vint.ast.parsing import Parser
from vint.ast.traversing import traverse


def prettify_node_type(node):
    node['type'] = NodeType(node['type'])


if __name__ == '__main__':
    parser = Parser()

    ast = parser.parse_file(Path(sys.argv[1]))

    traverse(ast, on_enter=prettify_node_type)

    pprint(ast)
