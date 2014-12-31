from vint.ast.traversing import traverse as _traverse_org, SKIP_CHILDREN
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

        _traverse_org(ast, on_enter=enter_handler)

        return ast


def get_redir_content(node):
    return node.get(REDIR_CONTENT)


def traverse(node, on_enter=None, on_leave=None):
    def enter_handler(node):
        if on_enter:
            returned = on_enter(node)
            if returned is SKIP_CHILDREN:
                return SKIP_CHILDREN

        if REDIR_CONTENT in node:
            traverse(node[REDIR_CONTENT], on_enter=on_enter, on_leave=on_leave)

    def leave_handler(node):
        if not on_leave:
            return

        return on_leave(node)

    _traverse_org(node, on_enter=enter_handler, on_leave=leave_handler)
