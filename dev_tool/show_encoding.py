#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

vint_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(vint_root))

from vint.encodings.decoder import Decoder
from vint.encodings.decoding_strategy import default_decoding_strategy


if __name__ == '__main__':
    arg_parser = ArgumentParser(prog='show_ast', description='Show AST')
    arg_parser.add_argument('file', nargs=1, help='File to detect encoding')
    namespace = vars(arg_parser.parse_args(sys.argv[1:]))

    file_path = Path(namespace['file'][0])
    decoder = Decoder(default_decoding_strategy)
    decoder.read(file_path)
    pprint(decoder.debug_hint)
