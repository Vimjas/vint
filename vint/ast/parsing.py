import extlib.vimlparser


class Parser(object):
    def __init__(self):
        pass

    def parse(self, string):
        lines = string.split('\n')

        reader = extlib.vimlparser.StringReader(lines)
        parser = extlib.vimlparser.VimLParser()
        ast = parser.parse(reader)
        return ast

    def parse_file(self, file_path):
        with open(file_path) as f:
            return self.parse(f.read())
