from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin.redir_assignment_parser import (
    RedirAssignmentParser,
    get_redir_content,
)
from vint.ast.plugin.scope_plugin.map_and_filter_parser import (
    MapAndFilterParser,
    get_string_expr_content,
)
from vint.ast.node_type import NodeType


IDENTIFIER_ATTRIBUTE = 'VINT:identifier_attribute'
IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG = 'is_declarative'
IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG = 'is_dynamic'
IDENTIFIER_ATTRIBUTE_MEMBER_FLAG = 'is_member'
IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG = 'is_function'
IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG = 'is_autoload'
IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG = 'is_declarative_parameter'
IDENTIFIER_ATTRIBUTE_STRING_EXPRESSION_CONTEXT = 'is_on_str_expr_context'
REFERENCING_IDENTIFIERS = 'VINT:referencing_identifiers'
DECLARING_IDENTIFIERS = 'VINT:declaring_identifiers'


DeclarativeNodeTypes = {
    NodeType.LET: True,
    NodeType.FUNCTION: True,
    NodeType.FOR: True,
    NodeType.EXCMD: True,
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
    This class classify nodes by 5 flags:

    - is dynamic: True if the identifier name can be determined by static analysis.
    - is member: True if the identifier is a member of a subscription/dot/slice node.
    - is declaring: True if the identifier is used to declare.
    - is autoload: True if the identifier is declared with autoload.
    - is function: True if the identifier is a function. Vim distinguish
        between function identifiers and variable identifiers.
    - is declarative paramter: True if the identifier is a declarative
        parameter. For example, the identifier "param" in Func(param) is a
        declarative paramter.
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
                    id_attr[IDENTIFIER_ATTRIBUTE_MEMBER_FLAG]:
                return

            if id_attr[IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG]:
                self.static_declaring_identifiers.append(node)
            else:
                self.static_referencing_identifiers.append(node)


    def attach_identifier_attributes(self, ast):
        """ Attach 5 flags to the AST.

        - is dynamic: True if the identifier name can be determined by static analysis.
        - is member: True if the identifier is a member of a subscription/dot/slice node.
        - is declaring: True if the identifier is used to declare.
        - is autoload: True if the identifier is declared with autoload.
        - is function: True if the identifier is a function. Vim distinguish
            between function identifiers and variable identifiers.
        - is declarative paramter: True if the identifier is a declarative
            parameter. For example, the identifier "param" in Func(param) is a
            declarative paramter.
        - is on string expression context: True if the variable is on the
            string expression context. The string expression context is the
            string content on the 2nd argument of the map or filter function.
        """
        redir_assignment_parser = RedirAssignmentParser()
        ast_with_parsed_redir = redir_assignment_parser.process(ast)

        map_and_filter_parser = MapAndFilterParser()
        ast_with_parse_map_and_filter_and_redir = \
            map_and_filter_parser.process(ast_with_parsed_redir)

        traverse(ast_with_parse_map_and_filter_and_redir,
                 on_enter=self._enter_handler)
        return ast


    def _set_identifier_attribute(self, node, is_declarative=None, is_dynamic=None,
                                  is_member=None, is_function=None, is_autoload=None,
                                  is_declarative_parameter=None,
                                  is_on_str_expr_context=None):
        id_attr = node.setdefault(IDENTIFIER_ATTRIBUTE, {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_STRING_EXPRESSION_CONTEXT: False,
        })

        if is_declarative is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG] = is_declarative

        if is_dynamic is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG] = is_dynamic

        if is_member is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_MEMBER_FLAG] = is_member

        if is_function is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG] = is_function

        if is_autoload is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG] = is_autoload

        if is_declarative_parameter is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG] = \
                is_declarative_parameter

        if is_on_str_expr_context is not None:
            id_attr[IDENTIFIER_ATTRIBUTE_STRING_EXPRESSION_CONTEXT] = \
                is_on_str_expr_context


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

        if node_type is NodeType.DELFUNCTION:
            self._enter_delfunction_node(node)
            return


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

                if NodeType(member_node['type']) is NodeType.IDENTIFIER:
                    # Only the identifier should be flagged as a member that
                    # the variable is an accessor for a list or dictionary.
                    # For example, the variable that is "l:end" in list[0 : l:end]
                    # is not accessor for the symbol table of the variable "list",
                    # but it is a variable symbol table accessor.
                    continue

                self._pre_mark_member_node(member_node)
            return

        member_node = node['right']
        if node_type is NodeType.SUBSCRIPT:
            if NodeType(member_node['type']) is NodeType.IDENTIFIER:
                # Only the identifier should be flagged as a member that
                # the variable is an accessor for a list or dictionary.
                # For example, the variable that is "l:key" in dict[l:key]
                # is not accessor for the symbol table of the variable "dict",
                # but it is a variable symbol table accessor.
                return

        self._pre_mark_member_node(member_node)


    def _pre_mark_member_node(self, member_node):
        member_node_type = NodeType(member_node['type'])

        if member_node_type in IdentifierTerminateNodeTypes or \
                member_node_type in AnalyzableSubScriptChildNodeTypes:
            self._set_identifier_attribute(member_node, is_member=True)


    def _enter_identifier_like_node(self, node, is_declarative=None,
                                    is_function=None, is_declarative_parameter=None,
                                    is_on_str_expr_context=None):
        node_type = NodeType(node['type'])

        if node_type in AccessorLikeNodeTypes:
            id_like_node = node
            self._enter_accessor_node(id_like_node,
                                      is_declarative=is_declarative,
                                      is_function=is_function,
                                      is_declarative_parameter=is_declarative_parameter,
                                      is_on_str_expr_context=is_on_str_expr_context)
            return

        if node_type in IdentifierTerminateNodeTypes:
            id_like_node = node
            self._enter_identifier_node(id_like_node,
                                        is_declarative=is_declarative,
                                        is_function=is_function,
                                        is_declarative_parameter=is_declarative_parameter,
                                        is_on_str_expr_context=is_on_str_expr_context)
            return

        # Curlyname node can have a dynamic name. For example:
        #   let s:var = 'VAR'
        #   let my_{s:var} = 0
        if node_type is NodeType.CURLYNAME:
            id_like_node = node
            self._enter_curlyname_node(id_like_node,
                                       is_declarative=is_declarative,
                                       is_function=is_function,
                                       is_declarative_parameter=is_declarative_parameter,
                                       is_on_str_expr_context=is_on_str_expr_context)
            return


    def _enter_function_node(self, func_node):
        # Function node has declarative identifiers as the function name and
        # the paramerter names.

        # Function name is in the left.
        func_name_node = func_node['left']
        self._enter_identifier_like_node(func_name_node,
                                         is_declarative=True,
                                         is_function=True)

        # Function parameter names are in the r_list.
        func_param_nodes = func_node['rlist']
        for func_param_node in func_param_nodes:
            self._enter_identifier_like_node(func_param_node,
                                             is_declarative_parameter=True,
                                             is_declarative=True)


    def _enter_delfunction_node(self, delfunc_node):
        func_name_node = delfunc_node['left']
        self._enter_identifier_like_node(func_name_node,
                                         is_function=True)


    def _enter_curlyname_node(self, curlyname_node, is_declarative=None, is_function=None,
                              is_declarative_parameter=None, is_on_str_expr_context=None):
        self._set_identifier_attribute(curlyname_node,
                                       is_dynamic=True,
                                       is_declarative=is_declarative,
                                       is_function=is_function,
                                       is_declarative_parameter=is_declarative_parameter,
                                       is_on_str_expr_context=is_on_str_expr_context)


    def _enter_identifier_node(self, id_node, is_declarative=None, is_function=None,
                               is_declarative_parameter=None, is_on_str_expr_context=None):
        is_autoload = '#' in id_node['value']
        self._set_identifier_attribute(id_node,
                                       is_declarative=is_declarative,
                                       is_autoload=is_autoload,
                                       is_function=is_function,
                                       is_declarative_parameter=is_declarative_parameter,
                                       is_on_str_expr_context=is_on_str_expr_context)


    def _enter_accessor_node(self, accessor_node, is_declarative=None,
                             is_function=None, is_declarative_parameter=None,
                             is_on_str_expr_context=None):
        accessor_node_type = NodeType(accessor_node['type'])

        if accessor_node_type is NodeType.DOT:
            self._set_identifier_attribute(accessor_node['right'],
                                           is_declarative=is_declarative,
                                           is_dynamic=False,
                                           is_function=is_function,
                                           is_declarative_parameter=is_declarative_parameter,
                                           is_on_str_expr_context=is_on_str_expr_context)
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
                                               is_declarative=is_declarative,
                                               is_dynamic=False,
                                               is_function=is_function,
                                               is_declarative_parameter=is_declarative_parameter,
                                               is_on_str_expr_context=is_on_str_expr_context)
            return

        if accessor_node_type is NodeType.SLICE:
            for elem_node in accessor_node['rlist']:
                if type(elem_node) is list:
                    # In VimLParser spec, an empty array means null.
                    #   list[1:] => {rlist: [node, []]}
                    continue

                elem_node_type = NodeType(elem_node['type'])

                # We can do static analysis NodeType.SLICE such as:
                #   let object[0:1] = 0
                #
                # but we cannot do it in other cases such as:
                #   let object[0:var] = 0
                is_dynamic = elem_node_type not in AnalyzableSubScriptChildNodeTypes

                # In the following case, 0 is a declarative but var is not declarative.
                # It is more like a reference.
                #   let object[0:var] = 0
                is_declarative = elem_node_type in AnalyzableSubScriptChildNodeTypes

                self._set_identifier_attribute(elem_node,
                                               is_declarative=is_declarative,
                                               is_dynamic=is_dynamic,
                                               is_function=is_function,
                                               is_declarative_parameter=is_declarative_parameter,
                                               is_on_str_expr_context=is_on_str_expr_context)
            return

        raise Exception()


    def _enter_let_node(self, let_node):
        # Only "=" operator can be used as declaration.
        if let_node['op'] != '=':
            return

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
                self._enter_identifier_like_node(elem_node, is_declarative=True)
        else:
            self._enter_identifier_like_node(left_node, is_declarative=True)

        rest_node = node['rest']
        has_rest = type(rest_node) is not list
        if has_rest:
            self._enter_identifier_like_node(rest_node, is_declarative=True)


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
        if node_type is NodeType.EXCMD:
            self._enter_excmd_node(node)
            return


    def _enter_call_node(self, call_node):
        left_node = call_node['left']
        self._enter_identifier_like_node(left_node, is_function=True)

        # Care the 2nd argument of the map or filter function.
        self._enter_str_expr_content_node(call_node)


    def _enter_str_expr_content_node(self, call_node):
        string_expr_content_nodes = get_string_expr_content(call_node)
        if not string_expr_content_nodes:
            return

        def enter_handler(node):
            self._enter_identifier_like_node(node, is_on_str_expr_context=True)

        for string_expr_content_node in string_expr_content_nodes:
            traverse(string_expr_content_node, on_enter=enter_handler)


    def _enter_excmd_node(self, cmd_node):
        # Care an assignment by using command ":redir"
        redir_content_node = get_redir_content(cmd_node)

        if not redir_content_node:
            return

        self._enter_identifier_like_node(redir_content_node, is_declarative=True)



def is_identifier_like_node(node):
    return IDENTIFIER_ATTRIBUTE in node


def is_function_identifier(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG]


def is_dynamic_identifier(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG]


def is_declarative_identifier(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG]


def is_member_identifier(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_MEMBER_FLAG]


def is_autoload_identifier(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG]


def is_declarative_parameter(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG]


def is_on_string_expression_context(node):
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_STRING_EXPRESSION_CONTEXT]
