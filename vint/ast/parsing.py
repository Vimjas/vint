import extlib.vimlparser
import chardet


class EncodingDetectionError(Exception):
    def __init__(self, file_path):
        self.file_path = file_path


    def __str__(self):
        return 'Cannot detect encoding (binary file?): {file_path}'.format(
            file_path=str(self.file_path))


class Parser(object):
    def __init__(self, plugins=None):
        """ Initialize Parser with the specified plugins.
        The plugins can add attributes to the AST.
        """
        self.plugins = plugins or []


    def parse(self, string):
        """ Parse vim script string and return the AST. """
        lines = string.split('\n')

        reader = extlib.vimlparser.StringReader(lines)
        parser = extlib.vimlparser.VimLParser()
        ast = parser.parse(reader)

        # TOPLEVEL does not have a pos, but we need pos for all nodes
        ast['pos'] = {'col': 1, 'i': 0, 'lnum': 1}

        for plugin in self.plugins:
            plugin.process(ast)

        return ast


    def parse_file(self, file_path):
        """ Parse vim script file and return the AST. """
        with file_path.open(mode='rb') as f:
            bytes_seq = f.read()
            encoding_hint = chardet.detect(bytes_seq)

            encoding = encoding_hint['encoding']
            if not encoding:
                # Falsey means we cannot detect the encoding of the file.
                raise EncodingDetectionError(file_path)

            decoded = bytes_seq.decode(encoding)
            return self.parse(decoded)
