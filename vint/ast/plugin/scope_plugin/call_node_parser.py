from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse, register_traverser_extension
from vint.ast.parsing import Parser

LAMBDA_STRING_EXPR_CONTENT = 'VINT:lambda_string_expression'
FUNCTION_REFERENCE_STRING_EXPR_CONTENT = 'VINT:function_reference_expression'
STRING_EXPR_CONTEXT = 'VINT:string_expression_context'
STRING_EXPR_CONTEXT_FLAG = 'is_on_string_expr'



class CallNodeParser(object):
    """ A class to make string expression in map and filter function parseable.
    """
    def process(self, ast):
        def enter_handler(node):
            node_type = NodeType(node['type'])
            if node_type is not NodeType.CALL:
                return

            called_function_identifier = node['left']

            # The name node type of "map" or "filter" or "call" are always IDENTIFIER.
            if NodeType(called_function_identifier['type']) is not NodeType.IDENTIFIER:
                return

            called_function_identifier_value = called_function_identifier.get('value')

            if called_function_identifier_value in ['map', 'filter']:
                # Analyze second argument of "map" or "filter" if the node type is STRING.
                self._attach_string_expr_content_to_map_or_func(node)
            elif called_function_identifier_value in ['call', 'function']:
                # Analyze first argument of "call" or "function" if the node type is STRING.
                self._attach_string_expr_content_to_call_or_function(node)

        traverse(ast, on_enter=enter_handler)

        return ast


    def _attach_string_expr_content_to_map_or_func(self, map_or_func_call_node):
        args = map_or_func_call_node['rlist']

        # Prevent crash. See https://github.com/Kuniwak/vint/issues/256.
        if len(args) < 2:
            return

        string_expr_node = args[1]

        # We can statically analyze only STRING nodes
        if NodeType(string_expr_node['type']) is not NodeType.STRING:
            return

        parser = Parser()
        string_expr_content_nodes = parser.parse_string_expr(string_expr_node)

        # Set a flag that means whether the expression is in other string literals.
        CallNodeParser._set_string_expr_context_flag(string_expr_content_nodes)

        string_expr_node[LAMBDA_STRING_EXPR_CONTENT] = string_expr_content_nodes


    @classmethod
    def _set_string_expr_context_flag(cls, string_expr_content_nodes):
        def enter_handler(node):
            # NOTE: We need this flag only string nodes, because this flag is only for
            # ProhibitUnnecessaryDoubleQuote.
            if NodeType(node['type']) is NodeType.STRING:
                node[STRING_EXPR_CONTEXT] = {
                    STRING_EXPR_CONTEXT_FLAG: True,
                }

        for string_expr_content_node in string_expr_content_nodes:
            traverse(string_expr_content_node, on_enter=enter_handler)

        return string_expr_content_nodes


    def _attach_string_expr_content_to_call_or_function(self, call_call_node):
        args = call_call_node['rlist']

        if len(args) < 1:
            return

        # We can statically analyze only STRING node
        string_expr_node = args[0]

        if NodeType(string_expr_node['type']) is not NodeType.STRING:
            return

        parser = Parser()
        string_expr_content_nodes = parser.parse_string_expr(string_expr_node)

        func_ref_nodes = list(filter(
            lambda node: NodeType(node['type']) is NodeType.IDENTIFIER,
            string_expr_content_nodes
        ))

        string_expr_node[FUNCTION_REFERENCE_STRING_EXPR_CONTENT] = func_ref_nodes


def get_lambda_string_expr_content(node):
    return node.get(LAMBDA_STRING_EXPR_CONTENT)


def get_function_reference_string_expr_content(node):
    return node.get(FUNCTION_REFERENCE_STRING_EXPR_CONTENT)


def is_on_string_expr_context(node):
    return node.get(STRING_EXPR_CONTEXT, {})\
        .get(STRING_EXPR_CONTEXT_FLAG, False)


@register_traverser_extension
def traverse_string_expr_content(node, on_enter=None, on_leave=None):
    lambda_string_expr_content_nodes = get_lambda_string_expr_content(node)
    if lambda_string_expr_content_nodes is not None:
        for child_node in lambda_string_expr_content_nodes:
            traverse(child_node, on_enter=on_enter, on_leave=on_leave)

    func_ref_string_expr_content_nodes = get_function_reference_string_expr_content(node)
    if func_ref_string_expr_content_nodes is not None:
        for child_node in func_ref_string_expr_content_nodes:
            traverse(child_node, on_enter=on_enter, on_leave=on_leave)
