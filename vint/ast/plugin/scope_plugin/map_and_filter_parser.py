from vint.ast.traversing import traverse, register_traverser_extension

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType

STRING_EXPR_CONTENT = 'VINT:string_expression'



class MapAndFilterParser(object):
    """ A class to make string expression in map and filter function parseable.
    """

    def process(self, ast):
        def enter_handler(node):
            node_type = NodeType(node['type'])
            if node_type is not NodeType.CALL:
                return

            called_function_identifier = node['left']
            is_map_or_function_call = called_function_identifier.get('value') in {
                'map': True,
                'filter': True,
            }

            if not is_map_or_function_call:
                return

            string_expr = node['rlist'][1]

            parser = Parser()
            string_expr_content_nodes = parser.parse_string_expr(string_expr)
            node[STRING_EXPR_CONTENT] = string_expr_content_nodes

        traverse(ast, on_enter=enter_handler)

        return ast


def get_string_expr_content(node):
    return node.get(STRING_EXPR_CONTENT)


@register_traverser_extension
def traverse_string_expr_content(node, on_enter=None, on_leave=None):
    string_expr_content_nodes = get_string_expr_content(node)
    if string_expr_content_nodes is None:
        return

    for child_node in string_expr_content_nodes:
        traverse(child_node, on_enter=on_enter, on_leave=on_leave)
