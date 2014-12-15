from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType


IDENTIFIER_ATTRIBUTE = 'VINT:identifier_attribute'
IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG = 'is_definition'
IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG = 'is_dynamic'
IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG = 'is_member_of_subscript'

DeclarativeNodeTypes = {
    NodeType.LET: True,
    NodeType.FUNCTION: True,
    NodeType.FOR: True,
}

IdentifierTerminateNodeTypes = {
    NodeType.IDENTIFIER: True,
    NodeType.ENV: True,
    NodeType.REG: True,
    NodeType.OPTION: True,
    NodeType.CURLYNAME: True,
}

AccessorLikeNodeTypes = {
    NodeType.DOT: True,
    NodeType.SUBSCRIPT: True,
    NodeType.SLICE: True,
}

# These node types is identifier-like when:
#   let object['name'] = 0
AnalyzableSubScriptChildNodeTypes = {
    NodeType.NUMBER: True,
    NodeType.STRING: True,
}


class IdentifierDefinitionMarker(object):
    def __init__(self):
        self.log = []

    def attach_identifier_attributes(self, ast):
        traverse(ast, on_enter=self._enter_handler)
        return ast


    def _set_identifier_attribute(self, node, is_definition=None, is_dynamic=None,
                                  is_member_of_subscript=None):

        if IDENTIFIER_ATTRIBUTE in node:
            id_attr = node[IDENTIFIER_ATTRIBUTE]
        else:
            id_attr = node[IDENTIFIER_ATTRIBUTE] = {
                IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: False,
                IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
                IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
            }

        if is_definition is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG] = is_definition

        if is_dynamic is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG] = is_dynamic

        if is_member_of_subscript is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG] = is_member_of_subscript


    def _enter_handler(self, node):
        node_type = NodeType(node['type'])

        if node_type in IdentifierTerminateNodeTypes:
            # Attach identifier attributes to all IdentifierTerminateNodeTypes.
            self._set_identifier_attribute(node)

        if node_type in AccessorLikeNodeTypes:
            self._pre_mark_accessor_children(node)

        if node_type in DeclarativeNodeTypes:
            self._enter_declarative_node(node)


    def _pre_mark_accessor_children(self, node):
        node_type = NodeType(node['type'])
        dict_node = node['left']

        if NodeType(dict_node['type']) in AccessorLikeNodeTypes:
            self._pre_mark_accessor_children(dict_node)

        if node_type is NodeType.SLICE:
            for member_node in node['rlist']:
                self._pre_mark_member_node(member_node)
        else:
            member_node = node['right']
            self._pre_mark_member_node(member_node)


    def _pre_mark_member_node(self, member_node):
        member_node_type = NodeType(member_node['type'])

        if member_node_type in IdentifierTerminateNodeTypes or \
                member_node_type in AnalyzableSubScriptChildNodeTypes:
            self._set_identifier_attribute(member_node, is_member_of_subscript=True)


    def _enter_definition_identifier_like_node(self, id_like_node):
        id_like_node_type = NodeType(id_like_node['type'])

        if id_like_node_type in AccessorLikeNodeTypes:
            self._enter_definition_accessor_node(id_like_node)
            return

        if id_like_node_type in IdentifierTerminateNodeTypes:
            self._enter_definition_identifier_node(id_like_node)
            return

        # We can not do static analysis NodeType.CURLYNAME, because it can
        # name dyamically.
        if id_like_node_type is NodeType.CURLYNAME:
            self._enter_definition_curlyname_node(id_like_node)
            return


    def _enter_function_node(self, func_node):
        func_name_node = func_node['left']
        self._enter_definition_identifier_like_node(func_name_node)

        func_param_nodes = func_node['rlist']
        for func_param_node in func_param_nodes:
            self._enter_definition_identifier_like_node(func_param_node)


    def _enter_definition_curlyname_node(self, curlyname_node):
        self._set_identifier_attribute(curlyname_node, is_dynamic=True)


    def _enter_definition_identifier_node(self, def_id_node):
        self._set_identifier_attribute(def_id_node, is_definition=True)


    def _enter_definition_accessor_node(self, accessor_node):
        accessor_node_type = NodeType(accessor_node['type'])

        if accessor_node_type is NodeType.DOT:
            self._set_identifier_attribute(accessor_node['right'],
                                           is_definition=True,
                                           is_dynamic=False)
            return

        if accessor_node_type is NodeType.SUBSCRIPT:
            subscript_right_type = NodeType(accessor_node['right']['type'])

            # We can do static analysis NodeType.SUBSCRIPT such as:
            #   let object['name'] = 0
            #
            # but we cannot it in other cases:
            #   let object[var] = 0
            is_dynamic = subscript_right_type not in AnalyzableSubScriptChildNodeTypes

            self._set_identifier_attribute(accessor_node['right'],
                                           is_definition=True,
                                           is_dynamic=is_dynamic)
            return

        if accessor_node_type is NodeType.SLICE:
            for elem_node in accessor_node['rlist']:
                elem_node_type = NodeType(elem_node['type'])

                # We can do static analysis NodeType.SLICE such as:
                #   let object[0:1] = 0
                #
                # but we cannot it in other cases:
                #   let object[0:var] = 0
                is_dynamic = elem_node_type not in AnalyzableSubScriptChildNodeTypes

                # In following case, 0 is definition but var is not definition.
                # It is more like a reference.
                #   let object[0:var] = 0
                is_definition = elem_node_type in AnalyzableSubScriptChildNodeTypes

                self._set_identifier_attribute(elem_node,
                                               is_definition=is_definition,
                                               is_dynamic=is_dynamic)
            return

        raise Exception()


    def _enter_let_node(self, let_node):
        self._enter_destructuring_assignment_node(let_node)


    def _enter_for_node(self, for_node):
        self._enter_destructuring_assignment_node(for_node)


    def _enter_destructuring_assignment_node(self, node):
        # In VimLParser spec, an empty array mean null.
        #
        # | Normal assignment    | Destructuring assignment    |
        # |:--------------------:|:---------------------------:|
        # | node['left'] == Node | node['left'] == []          |
        # | node['list'] == []   | node['list'] == [Node, ...] |

        left_node = node['left']
        is_destructuring_assignment = type(left_node) is list

        if is_destructuring_assignment:
            for elem_node in node['list']:
                self._enter_definition_identifier_like_node(elem_node)
        else:
            self._enter_definition_identifier_like_node(left_node)


    def _enter_declarative_node(self, node):
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            self._enter_function_node(node)
            return
        if node_type is NodeType.LET:
            self._enter_let_node(node)
            return
        if node_type is NodeType.FOR:
            self._enter_for_node(node)
            return
