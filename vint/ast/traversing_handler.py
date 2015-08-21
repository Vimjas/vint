from vint.ast.node_type import get_node_type, NodeType
from vint.ast.traversing import traverse


def _combine(funcs):
    def combined_funcs(node):
        for method in funcs:
            method(node)
    return combined_funcs


def compose_handlers(*handlers):
    composed_handler = {}

    for node_type in NodeType:
        funcs = [handler[node_type] for handler in handlers if node_type in handler]
        composed_handler[node_type] = _combine(funcs)

    return composed_handler


def traverse_by_handler(ast, on_enter=None, on_leave=None):
    """ Traverse the specified AST by NodeType-to-function dictionary.

    USAGE:
        traverse_by_handler(ast, on_enter={ NodeType.ECHO: handlerFn })
    """

    def create_caller(handler):
        if handler is None:
            return None

        def caller(node):
            node_type = get_node_type(node)

            if node_type not in handler:
                return

            method = handler[node_type]
            method(node)

        return caller

    traverse(ast,
             on_enter=create_caller(on_enter),
             on_leave=create_caller(on_leave))
