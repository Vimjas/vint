# Low-level API for parsing Vim script without using any parse plugins.
import extlib.vimlparser
from vint.encoding import guess_encoding


def parse(string):
    """ Parse vim script string and return the AST. """
    lines = string.split('\n')

    reader = extlib.vimlparser.StringReader(lines)
    parser = extlib.vimlparser.VimLParser()
    ast = parser.parse(reader)

    # TOPLEVEL does not have a pos, but we need pos for all nodes
    ast['pos'] = {'col': 1, 'i': 0, 'lnum': 1}

    return ast


def parse_file(file_path):
    with file_path.open(mode='rb') as f:
        bytes_seq = f.read()

        is_empty = len(bytes_seq) == 0
        if is_empty:
            return parse('')

        encoding = guess_encoding(bytes_seq, file_path)

        decoded = bytes_seq.decode(encoding)
        decoded_and_lf_normalized = decoded.replace('\r\n', '\n')

        return parse(decoded_and_lf_normalized)
