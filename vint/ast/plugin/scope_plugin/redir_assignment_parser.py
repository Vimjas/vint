from vint.ast.traversing import traverse, register_traverser_extension

from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType

REDIR_CONTENT = 'VINT:redir_content'



class RedirAssignmentParser(object):
    """ A class to make redir assignment parseable. """


    def process(self, ast):
        def enter_handler(node):
            node_type = NodeType(node['type'])
            if node_type is not NodeType.EXCMD:
                return

            is_redir_command = node['ea']['cmd'].get('name') == 'redir'
            if not is_redir_command:
                return

            redir_cmd_str = node['str']
            is_redir_assignment = '=>' in redir_cmd_str
            if not is_redir_assignment:
                return

            parser = Parser()
            redir_content_node = parser.parse_redir(node)
            node[REDIR_CONTENT] = redir_content_node

        traverse(ast, on_enter=enter_handler)

        return ast


def get_redir_content(node):
    return node.get(REDIR_CONTENT)



@register_traverser_extension
def traverse_redir_content(node, on_enter=None, on_leave=None):
    if REDIR_CONTENT not in node:
        return

    traverse(node[REDIR_CONTENT], on_enter=on_enter, on_leave=on_leave)
