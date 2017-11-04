#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

vint_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(vint_root))

from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.parsing import Parser


def prettify_node_type(node):
    node['type'] = NodeType(node['type'])


if __name__ == '__main__':
    arg_parser = ArgumentParser(prog='show_ast', description='Show AST')
    arg_parser.add_argument('--enable-neovim', action='store_true', help='Enable Neovim syntax')
    arg_parser.add_argument('files', nargs='*', help='File to parse')
    namespace = vars(arg_parser.parse_args(sys.argv[1:]))

    filepaths = map(Path, namespace['files'])
    enable_neovim = namespace['enable_neovim']

    parser = Parser(enable_neovim=enable_neovim)

    for filepath in filepaths:
        ast = parser.parse_file(filepath)
        traverse(ast, on_enter=prettify_node_type)
        pprint(ast)
