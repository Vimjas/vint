#!/usr/bin/env python3

import chardet
import sys
from pprint import pprint
from pathlib import Path
from argparse import ArgumentParser


def main(file_path):
    # type: (Path) -> None
    with file_path.open(mode='rb') as f:
        bytes_seq = f.read()

        coding_hint = chardet.detect(bytes_seq)
        pprint(coding_hint)


if __name__ == '__main__':
    arg_parser = ArgumentParser(prog='show_ast', description='Show AST')
    arg_parser.add_argument('file', nargs=1, help='File to parse')
    namespace = vars(arg_parser.parse_args(sys.argv[1:]))

    main(Path(namespace['file'][0]))