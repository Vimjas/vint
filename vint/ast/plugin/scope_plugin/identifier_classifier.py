from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType


IDENTIFIER_ATTRIBUTE = 'VINT:identifier_attribute'
IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG = 'is_definition'
IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG = 'is_dynamic'
IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG = 'is_member_of_subscript'
IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG = 'is_function'
REFERENCING_IDENTIFIERS = 'VINT:referencing_identifiers'
DECLARING_IDENTIFIERS = 'VINT:declaring_identifiers'


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


class IdentifierClassifier(object):
    """ A class for identifier classifiers.
    This class classify nodes by 3 flags:

    - is dynamic: True if the identifier name can be determined by static analysis.
    - is member: True if the identifier is a member of a subscription/dot/slice node.
    - is declaring: True if the identifier is used to declare.
    """

    class IdentifierCollector(object):
        """ A class for identifier node collectors.
        Only static and not member nodes will be collected and the nodes will
        be grouped by 2 types; declaring or referencing.
        """

        def collect_identifiers(self, ast):
            self.static_referencing_identifiers = []
            self.static_declaring_identifiers = []

            # TODO: Make more performance efficiency.
            traverse(ast, on_enter=self._enter_handler)

            return {
                'static_declaring_identifiers': self.static_declaring_identifiers,
                'static_referencing_identifiers': self.static_referencing_identifiers,
            }


        def _enter_handler(self, node):
            is_identifier_like_node = IDENTIFIER_ATTRIBUTE in node

            if not is_identifier_like_node:
                return

            id_attr = node[IDENTIFIER_ATTRIBUTE]
            if id_attr[IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG] or \
                    id_attr[IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG]:
                return

            if id_attr[IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG]:
                self.static_declaring_identifiers.append(node)
            else:
                self.static_referencing_identifiers.append(node)


    def attach_identifier_attributes(self, ast):
        """ Attach 3 flags to the AST.

        - is dynamic: True if the identifier name can be determined by static analysis.
        - is member: True if the identifier is a member of a subscription/dot/slice node.
        - is declaring: True if the identifier is used to declare.
        - is function: True if the identifier is a function. Vim distinguish
                       between function identifiers and variable identifiers.
        """
        traverse(ast, on_enter=self._enter_handler)
        return ast


    def _set_identifier_attribute(self, node, is_definition=None, is_dynamic=None,
                                  is_member_of_subscript=None, is_function=None):

        id_attr = node.setdefault(IDENTIFIER_ATTRIBUTE, {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
        })

        if is_definition is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG] = is_definition

        if is_dynamic is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG] = is_dynamic

        if is_member_of_subscript is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG] = is_member_of_subscript

        if is_function is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG] = is_function


    def _enter_handler(self, node):
        node_type = NodeType(node['type'])

        if node_type in IdentifierTerminateNodeTypes:
            # Attach identifier attributes to all IdentifierTerminateNodeTypes.
            self._set_identifier_attribute(node)

        if node_type in AccessorLikeNodeTypes:
            self._pre_mark_accessor_children(node)

        if node_type in DeclarativeNodeTypes:
            self._enter_declarative_node(node)

        if node_type is NodeType.CALL:
            self._enter_call_node(node)


    def _pre_mark_accessor_children(self, node):
        node_type = NodeType(node['type'])
        dict_node = node['left']

        if NodeType(dict_node['type']) in AccessorLikeNodeTypes:
            self._pre_mark_accessor_children(dict_node)

        if node_type is NodeType.SLICE:
            for member_node in node['rlist']:
                # In VimLParser spec, an empty array means null.
                #   list[1:] => {rlist: [node, []]}
                if type(member_node) is list:
                    continue

                self._pre_mark_member_node(member_node)
        else:
            member_node = node['right']
            self._pre_mark_member_node(member_node)


    def _pre_mark_member_node(self, member_node):
        member_node_type = NodeType(member_node['type'])

        if member_node_type in IdentifierTerminateNodeTypes or \
                member_node_type in AnalyzableSubScriptChildNodeTypes:
            self._set_identifier_attribute(member_node,
                                           is_member_of_subscript=True)


    def _enter_identifier_like_node(self, id_like_node, is_definition=None,
                                    is_function=None):
        id_like_node_type = NodeType(id_like_node['type'])

        if id_like_node_type in AccessorLikeNodeTypes:
            self._enter_accessor_node(id_like_node,
                                      is_definition=is_definition,
                                      is_function=is_function)
            return

        if id_like_node_type in IdentifierTerminateNodeTypes:
            self._enter_identifier_node(id_like_node,
                                        is_definition=is_definition,
                                        is_function=is_function)
            return

        # Curlyname node can have a dynamic name. For example:
        #   let s:var = 'VAR'
        #   let my_{s:var} = 0
        if id_like_node_type is NodeType.CURLYNAME:
            self._enter_curlyname_node(id_like_node,
                                       is_definition=is_definition,
                                       is_function=is_function)
            return


    def _enter_function_node(self, func_node):
        # Function node has declarative identifiers as the function name and
        # the paramerter names.

        # Function name is in the left.
        func_name_node = func_node['left']
        self._enter_identifier_like_node(func_name_node,
                                         is_definition=True,
                                         is_function=True)

        # Function parameter names is in the r_list.
        func_param_nodes = func_node['rlist']
        for func_param_node in func_param_nodes:
            self._enter_identifier_like_node(func_param_node,
                                             is_definition=True)


    def _enter_curlyname_node(self, curlyname_node, is_definition=None, is_function=None):
        self._set_identifier_attribute(curlyname_node,
                                       is_dynamic=True,
                                       is_definition=is_definition,
                                       is_function=is_function)


    def _enter_identifier_node(self, def_id_node, is_definition=None, is_function=None):
        self._set_identifier_attribute(def_id_node,
                                       is_definition=is_definition,
                                       is_function=is_function)


    def _enter_accessor_node(self, accessor_node, is_definition=None, is_function=None):
        accessor_node_type = NodeType(accessor_node['type'])

        if accessor_node_type is NodeType.DOT:
            self._set_identifier_attribute(accessor_node['right'],
                                           is_definition=is_definition,
                                           is_dynamic=False,
                                           is_function=is_function)
            return

        if accessor_node_type is NodeType.SUBSCRIPT:
            subscript_right_type = NodeType(accessor_node['right']['type'])

            # We can do static analysis NodeType.SUBSCRIPT such as:
            #   let object['name'] = 0
            #
            # but we cannot do it in other cases such as:
            #   let object[var] = 0
            is_dynamic = subscript_right_type not in AnalyzableSubScriptChildNodeTypes

            if not is_dynamic:
                self._set_identifier_attribute(accessor_node['right'],
                                               is_definition=is_definition,
                                               is_dynamic=False,
                                               is_function=is_function)
            return

        if accessor_node_type is NodeType.SLICE:
            for elem_node in accessor_node['rlist']:
                elem_node_type = NodeType(elem_node['type'])

                # We can do static analysis NodeType.SLICE such as:
                #   let object[0:1] = 0
                #
                # but we cannot do it in other cases such as:
                #   let object[0:var] = 0
                is_dynamic = elem_node_type not in AnalyzableSubScriptChildNodeTypes

                # In the following case, 0 is a definition but var is not definition.
                # It is more like a reference.
                #   let object[0:var] = 0
                is_definition = elem_node_type in AnalyzableSubScriptChildNodeTypes

                self._set_identifier_attribute(elem_node,
                                               is_definition=is_definition,
                                               is_dynamic=is_dynamic,
                                               is_function=is_function)
            return

        raise Exception()


    def _enter_let_node(self, let_node):
        self._enter_destructuring_assignment_node(let_node)


    def _enter_for_node(self, for_node):
        self._enter_destructuring_assignment_node(for_node)


    def _enter_destructuring_assignment_node(self, node):
        # In VimLParser spec, an empty array means null.
        #
        # | Normal assignment    | Destructuring assignment    |
        # |:--------------------:|:---------------------------:|
        # | node['left'] == Node | node['left'] == []          |
        # | node['list'] == []   | node['list'] == [Node, ...] |

        left_node = node['left']
        is_destructuring_assignment = type(left_node) is list

        if is_destructuring_assignment:
            for elem_node in node['list']:
                self._enter_identifier_like_node(elem_node, is_definition=True)
        else:
            self._enter_identifier_like_node(left_node, is_definition=True)


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


    def _enter_call_node(self, call_node):
        left_node = call_node['left']
        self._enter_identifier_like_node(left_node, is_function=True)
