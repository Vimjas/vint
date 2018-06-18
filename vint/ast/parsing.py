import re
from vint._bundles import vimlparser
from vint.ast.traversing import traverse
from vint.encodings.decoder import Decoder
from vint.encodings.decoding_strategy import default_decoding_strategy


class Parser(object):
    def __init__(self, plugins=None, enable_neovim=False):
        """ Initialize Parser with the specified plugins.
        The plugins can add attributes to the AST.
        """
        self.plugins = plugins.values() if plugins else []
        self._enable_neovim = enable_neovim


    def parse(self, string):
        """ Parse vim script string and return the AST. """
        lines = string.split('\n')

        reader = vimlparser.StringReader(lines)
        parser = vimlparser.VimLParser(self._enable_neovim)
        ast = parser.parse(reader)

        # TOPLEVEL does not have a pos, but we need pos for all nodes
        ast['pos'] = {'col': 1, 'i': 0, 'lnum': 1}

        for plugin in self.plugins:
            plugin.process(ast)

        return ast


    def parse_file(self, file_path):
        """ Parse vim script file and return the AST. """
        decoder = Decoder(default_decoding_strategy)
        decoded = decoder.read(file_path)
        decoded_and_lf_normalized = decoded.replace('\r\n', '\n')

        return self.parse(decoded_and_lf_normalized)


    def parse_redir(self, redir_cmd):
        """ Parse a command :redir content. """
        redir_cmd_str = redir_cmd['str']

        matched = re.match(r'redir?!?\s*(=>>?\s*)(\S+)', redir_cmd_str)
        if matched:
            redir_cmd_op = matched.group(1)
            redir_cmd_body = matched.group(2)

            arg_pos = redir_cmd['ea']['argpos']

            # Position of the "redir_cmd_body"
            start_pos = {
                'col': arg_pos['col'] + len(redir_cmd_op),
                'i': arg_pos['i'] + len(redir_cmd_op),
                'lnum': arg_pos['lnum'],
            }

            # NOTE: This is a hack to parse variable node.
            raw_ast = self.parse('echo ' + redir_cmd_body)

            # We need the left node of ECHO node
            redir_cmd_ast = raw_ast['body'][0]['list'][0]

            def adjust_position(node):
                pos = node['pos']
                # Care 1-based index and the length of "echo ".
                pos['col'] += start_pos['col'] - 1 - 5

                # Care the length of "echo ".
                pos['i'] += start_pos['i'] - 5

                # Care 1-based index
                pos['lnum'] += start_pos['lnum'] - 1

            traverse(redir_cmd_ast, on_enter=adjust_position)

            return redir_cmd_ast

        return None


    def parse_string_expr(self, string_expr_node):
        """ Parse a string node content. """
        string_expr_node_value = string_expr_node['value']
        string_expr_str = string_expr_node_value[1:-1]

        # Care escaped string literals
        if string_expr_node_value[0] == "'":
            string_expr_str = string_expr_str.replace("''", "'")
        else:
            string_expr_str = string_expr_str.replace('\\"', '"')

        # NOTE: This is a hack to parse expr1. See :help expr1
        raw_ast = self.parse('echo ' + string_expr_str)

        # We need the left node of ECHO node
        parsed_string_expr_nodes = raw_ast['body'][0]['list']

        start_pos = string_expr_node['pos']

        def adjust_position(node):
            pos = node['pos']

            # Care 1-based index and the length of "echo ".
            pos['col'] += start_pos['col'] - 1 - 5

            # Care the length of "echo ".
            pos['i'] += start_pos['i'] - 5

            # Care 1-based index
            pos['lnum'] += start_pos['lnum'] - 1

        for parsed_string_expr_node in parsed_string_expr_nodes:
            traverse(parsed_string_expr_node, on_enter=adjust_position)

        return parsed_string_expr_nodes
