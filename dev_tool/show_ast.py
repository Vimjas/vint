#!/usr/bin/env python

import sys
from pathlib import Path
from pprint import pprint

vint_root = Path(__file__).resolve().parent.parent
sys.path.append(str(vint_root))

from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.parsing import Parser


def prettify_node_type(node):
    node['type'] = NodeType(node['type'])


if __name__ == '__main__':
    ast = Parser().parse_file(Path(sys.argv[1]))

    traverse(ast, on_enter=prettify_node_type)

    pprint(ast)
