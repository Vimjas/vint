from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse, register_traverser_extension
from vint.ast.parsing import Parser

STRING_EXPR_CONTENT = 'VINT:string_expression'
STRING_EXPR_CONTEXT = 'VINT:string_expression_context'



class MapAndFilterParser(object):
    """ A class to make string expression in map and filter function parseable. """
    def process(self, ast):
        def enter_handler(node):
            node_type = NodeType(node['type'])
            if node_type is not NodeType.CALL:
                return

            called_function_identifier = node['left']

            # Name node of the "map" or "filter" functions are always IDENTIFIER.
            if NodeType(called_function_identifier['type']) is not NodeType.IDENTIFIER:
                return

            is_map_or_function_call = called_function_identifier.get('value') in {
                'map': True,
                'filter': True,
            }

            if not is_map_or_function_call:
                return

            args = node['rlist']

            # Prevent crash. See https://github.com/Kuniwak/vint/issues/256.
            if len(args) < 2:
                return

            string_expr_node = args[1]

            # We can analyze only STRING nodes by static analyzing.
            if NodeType(string_expr_node['type']) is not NodeType.STRING:
                return

            string_expr_content_nodes = MapAndFilterParser._parse_string_expr_content_nodes(string_expr_node)
            node[STRING_EXPR_CONTENT] = string_expr_content_nodes

        traverse(ast, on_enter=enter_handler)

        return ast


    @classmethod
    def _parse_string_expr_content_nodes(cls, string_expr_node):
        parser = Parser()
        string_expr_content_nodes = parser.parse_string_expr(string_expr_node)

        def enter_handler(node):
            # NOTE: We need this flag only string nodes, because this flag is only for
            # ProhibitUnnecessaryDoubleQuote.
            if NodeType(node['type']) is NodeType.STRING:
                node[STRING_EXPR_CONTEXT] = {
                    'is_on_str_expr_context': True,
                }

        for string_expr_content_node in string_expr_content_nodes:
            traverse(string_expr_content_node, on_enter=enter_handler)

        return string_expr_content_nodes


def get_string_expr_content(node):
    return node.get(STRING_EXPR_CONTENT)


def get_string_context(node):
    return node.get(STRING_EXPR_CONTEXT, {
        'is_on_str_expr_context': False,
    })


@register_traverser_extension
def traverse_string_expr_content(node, on_enter=None, on_leave=None):
    string_expr_content_nodes = get_string_expr_content(node)
    if string_expr_content_nodes is None:
        return

    for child_node in string_expr_content_nodes:
        traverse(child_node, on_enter=on_enter, on_leave=on_leave)
