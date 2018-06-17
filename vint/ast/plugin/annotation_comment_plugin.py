from typing import Optional, List, Dict, Any
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.plugin.abstract_ast_plugin import AbstractASTPlugin


POSTFIX_COMMENT = 'VINT:postfix_comment'
POSTFIX_COMMENT_FLAG = 'VINT:is_postfix_comment'


class PostfixCommentPlugin(AbstractASTPlugin):
    def __init__(self):
        super(PostfixCommentPlugin, self).__init__()

        self._current_line = None  # type: Optional[int]
        self._nodes_in_current_line = None  # type: Optional[List[Dict[str, Any]]]


    def process(self, ast):
        self._current_line = 0
        self._nodes_in_current_line = []
        traverse(ast, on_enter=self._on_enter)


    def _on_enter(self, node):
        line = node['pos']['lnum']

        if line > self._current_line:
            PostfixCommentPlugin._attach_postfix_comment_if_necessary(self._nodes_in_current_line)
            self._current_line = line
            self._nodes_in_current_line = [node]
        else:
            self._nodes_in_current_line.append(node)


    @classmethod
    def _attach_postfix_comment_if_necessary(cls, nodes_at_line):
        if len(nodes_at_line) <= 1:
            return

        last_node_at_line = nodes_at_line[-1]
        if NodeType(last_node_at_line['type']) is not NodeType.COMMENT:
            return

        last_node_at_line[POSTFIX_COMMENT_FLAG] = True

        for node_at_line in nodes_at_line[0:-1]:
            node_at_line[POSTFIX_COMMENT] = last_node_at_line


def get_postfix_comment(node):
    return node.get(POSTFIX_COMMENT, None)


def is_postfix_comment(node):
    return node.get(POSTFIX_COMMENT_FLAG, False)


def has_postfix_comment(node):
    return POSTFIX_COMMENT in node
