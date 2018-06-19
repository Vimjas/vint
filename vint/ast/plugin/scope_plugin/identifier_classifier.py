from typing import List, Dict, Any
from vint.ast.traversing import traverse, SKIP_CHILDREN
from vint.ast.plugin.scope_plugin.redir_assignment_parser import (
    RedirAssignmentParser,
    get_redir_content,
)
from vint.ast.plugin.scope_plugin.call_node_parser import (
    CallNodeParser,
    get_lambda_string_expr_content,
    get_function_reference_string_expr_content,
)
from vint.ast.plugin.scope_plugin.identifier_attribute import (
    is_identifier_like_node as _is_identifier_like_node,
    is_dynamic_identifier as _is_dynamic_identifier,
    is_member_identifier as _is_member_identifier,
    is_variadic_symbol as _is_variadic_symbol,
    is_declarative_identifier as _is_declarative_identifier,
    set_identifier_attribute as _set_identifier_attribute,
)
from vint.ast.node_type import NodeType


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




class CollectedIdentifiers:
    def __init__(self, statically_declared_identifiers, statically_referencing_identifiers):
        # type: (List[Dict[str, Any]], List[Dict[str, Any]]) -> None
        self.statically_declared_identifiers = statically_declared_identifiers
        self.statically_referencing_identifiers = statically_referencing_identifiers


class IdentifierClassifier(object):
    """ A class for identifier classifiers.
    This class classify nodes by 5 flags:

    - is dynamic: True if the identifier name can be determined by static analysis.
    - is member: True if the identifier is a member of a subscription/dot/slice node.
    - is declaring: True if the identifier is used to declare.
    - is autoload: True if the identifier is declared with autoload.
    - is function: True if the identifier is a function. Vim distinguish
        between function identifiers and variable identifiers.
    - is declarative parameter: True if the identifier is a declarative
        parameter. For example, the identifier "param" in Func(param) is a
        declarative parameter.
    """

    class IdentifierCollector(object):
        """ A class for identifier node collectors.
        Only static and not member nodes will be collected and the nodes will
        be grouped by 2 types; declaring or referencing.
        """

        def __init__(self):
            self._static_referencing_identifiers = None  # type: List[Dict[str, Any]]
            self._static_declaring_identifiers = None  # type: List[Dict[str, Any]]


        def collect_identifiers(self, ast): # type: (Dict[str, Any]) -> CollectedIdentifiers
            self._static_referencing_identifiers = []
            self._static_declaring_identifiers = []

            # TODO: Make more performance efficiency.
            traverse(ast, on_enter=self._enter_handler)

            return CollectedIdentifiers(
                self._static_declaring_identifiers,
                self._static_referencing_identifiers
            )


        def _enter_handler(self, node):
            if not _is_identifier_like_node(node):
                return

            # FIXME: Dynamic identifiers should be returned and it should be filtered by the caller.
            if _is_dynamic_identifier(node) or _is_member_identifier(node) or _is_variadic_symbol(node):
                return

            if _is_declarative_identifier(node):
                self._static_declaring_identifiers.append(node)
            else:
                self._static_referencing_identifiers.append(node)


    def attach_identifier_attributes(self, ast): # type: (Dict[str, Any]) -> Dict[str, Any]
        """ Attach 5 flags to the AST.

        - is dynamic: True if the identifier name can be determined by static analysis.
        - is member: True if the identifier is a member of a subscription/dot/slice node.
        - is declaring: True if the identifier is used to declare.
        - is autoload: True if the identifier is declared with autoload.
        - is function: True if the identifier is a function. Vim distinguish
            between function identifiers and variable identifiers.
        - is declarative parameter: True if the identifier is a declarative
            parameter. For example, the identifier "param" in Func(param) is a
            declarative parameter.
        - is on string expression context: True if the variable is on the
            string expression context. The string expression context is the
            string content on the 2nd argument of the map or filter function.
        - is lambda argument: True if the identifier is a lambda argument.
        """
        redir_assignment_parser = RedirAssignmentParser()
        ast_with_parsed_redir = redir_assignment_parser.process(ast)

        map_and_filter_parser = CallNodeParser()
        ast_with_parse_map_and_filter_and_redir = \
            map_and_filter_parser.process(ast_with_parsed_redir)

        traverse(
            ast_with_parse_map_and_filter_and_redir,
            on_enter=lambda node: self._enter_handler(
                node,
                is_on_lambda_str=None,
                is_on_lambda_body=None,
            )
        )
        return ast


    def _enter_handler(self, node, is_on_lambda_body, is_on_lambda_str):
        node_type = NodeType(node['type'])

        if node_type in IdentifierTerminateNodeTypes:
            # Attach identifier attributes to all IdentifierTerminateNodeTypes.
            self._enter_identifier_terminate_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        if node_type in AccessorLikeNodeTypes:
            self._pre_mark_accessor_children(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        if node_type in DeclarativeNodeTypes:
            self._enter_declarative_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        if node_type is NodeType.CALL:
            self._enter_call_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body
            )

        if node_type is NodeType.DELFUNCTION:
            self._enter_delfunction_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body
            )

        if node_type is NodeType.STRING:
            self._enter_string_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body
            )

        if node_type is NodeType.LAMBDA:
            return self._enter_lambda_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )


    def _pre_mark_accessor_children(self, node, is_on_lambda_body, is_on_lambda_str):
        node_type = NodeType(node['type'])
        dict_node = node['left']

        if NodeType(dict_node['type']) in AccessorLikeNodeTypes:
            self._pre_mark_accessor_children(
                dict_node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

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

                self._pre_mark_member_node(
                    member_node,
                    is_on_lambda_str=is_on_lambda_str,
                    is_on_lambda_body=is_on_lambda_body,
                )
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

        self._pre_mark_member_node(
            member_node,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
        )


    def _pre_mark_member_node(self, member_node, is_on_lambda_body, is_on_lambda_str):
        member_node_type = NodeType(member_node['type'])

        if member_node_type in IdentifierTerminateNodeTypes or \
                member_node_type in AnalyzableSubScriptChildNodeTypes:
            _set_identifier_attribute(
                member_node,
                is_member=True,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )


    def _enter_identifier_like_node(self, node, is_on_lambda_body, is_on_lambda_str, is_declarative=None,
                                    is_function=None, is_declarative_parameter=None):
        node_type = NodeType(node['type'])

        if node_type in AccessorLikeNodeTypes:
            id_like_node = node
            self._enter_accessor_node(
                id_like_node,
                is_declarative=is_declarative,
                is_function=is_function,
                is_declarative_parameter=is_declarative_parameter,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )
            return

        if node_type in IdentifierTerminateNodeTypes:
            id_like_node = node
            self._enter_identifier_terminate_node(
                id_like_node,
                is_declarative=is_declarative,
                is_function=is_function,
                is_declarative_parameter=is_declarative_parameter,
                is_on_lambda_body=is_on_lambda_body,
                is_on_lambda_str=is_on_lambda_str,
            )
            return


    def _enter_function_node(self, func_node, is_on_lambda_body, is_on_lambda_str):
        # Function node has declarative identifiers as the function name and
        # the parameter names.

        # Function name is in the left.
        func_name_node = func_node['left']
        self._enter_identifier_like_node(
            func_name_node,
            is_declarative=True,
            is_function=True,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
        )

        # Function parameter names are in the r_list.
        func_param_nodes = func_node['rlist']
        for func_param_node in func_param_nodes:
            self._enter_identifier_like_node(
                func_param_node,
                is_declarative_parameter=True,
                is_declarative=True,
                is_on_lambda_body=is_on_lambda_body,
                is_on_lambda_str=is_on_lambda_str,
            )


    def _enter_delfunction_node(self, delfunc_node, is_on_lambda_body, is_on_lambda_str):
        func_name_node = delfunc_node['left']
        self._enter_identifier_like_node(
            func_name_node,
            is_function=True,
            is_on_lambda_body=is_on_lambda_body,
            is_on_lambda_str=is_on_lambda_str
        )


    def _enter_curlyname_node(self, curlyname_node, is_on_lambda_body, is_on_lambda_str,
                              is_declarative=None, is_function=None, is_declarative_parameter=None):
        # Curlyname node can have a dynamic name. For example:
        #   let s:var = 'VAR'
        #   let my_{s:var} = 0
        _set_identifier_attribute(
            curlyname_node,
            is_dynamic=True,
            is_declarative=is_declarative,
            is_function=is_function,
            is_declarative_parameter=is_declarative_parameter,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
        )


    def _enter_identifier_terminate_node(self, id_term_node, is_on_lambda_body, is_on_lambda_str, is_declarative=None,
                                         is_function=None, is_declarative_parameter=None, is_lambda_argument=None):
        node_type = NodeType(id_term_node['type'])

        if node_type is NodeType.CURLYNAME:
            self._enter_curlyname_node(
                id_term_node,
                is_on_lambda_body=is_on_lambda_body,
                is_on_lambda_str=is_on_lambda_str,
                is_declarative=is_declarative,
                is_function=is_function,
                is_declarative_parameter=is_declarative_parameter,
            )
            return

        is_autoload = '#' in id_term_node['value']
        is_variadic = id_term_node['value'] == '...'
        _set_identifier_attribute(
            id_term_node,
            is_lambda_argument=is_lambda_argument,
            is_on_lambda_body=is_on_lambda_body,
            is_on_lambda_str=is_on_lambda_str,
            is_declarative=is_declarative,
            is_autoload=is_autoload,
            is_function=is_function,
            is_declarative_parameter=is_declarative_parameter,
            is_variadic=is_variadic,
        )


    def _enter_accessor_node(self, accessor_node, is_on_lambda_body, is_on_lambda_str, is_declarative=None,
                             is_function=None, is_declarative_parameter=None):
        accessor_node_type = NodeType(accessor_node['type'])

        if accessor_node_type is NodeType.DOT:
            _set_identifier_attribute(
                accessor_node['right'],
                is_declarative=is_declarative,
                is_dynamic=False,
                is_function=is_function,
                is_declarative_parameter=is_declarative_parameter,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )
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
                _set_identifier_attribute(
                    accessor_node['right'],
                    is_declarative=is_declarative,
                    is_dynamic=False,
                    is_function=is_function,
                    is_declarative_parameter=is_declarative_parameter,
                    is_on_lambda_str=is_on_lambda_str,
                    is_on_lambda_body=is_on_lambda_body,
                )
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

                _set_identifier_attribute(
                    elem_node,
                    is_declarative=is_declarative,
                    is_dynamic=is_dynamic,
                    is_function=is_function,
                    is_declarative_parameter=is_declarative_parameter,
                    is_on_lambda_str=is_on_lambda_str,
                    is_on_lambda_body=is_on_lambda_body,
                )
            return

        raise Exception()


    def _enter_let_node(self, let_node, is_on_lambda_body, is_on_lambda_str):
        # Only "=" operator can be used as declaration.
        if let_node['op'] != '=':
            return

        self._enter_assignment_node(
            let_node,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
        )


    def _enter_for_node(self, for_node, is_on_lambda_body, is_on_lambda_str):
        self._enter_assignment_node(
            for_node,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
        )


    def _enter_assignment_node(self, node, is_on_lambda_body, is_on_lambda_str):
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
                self._enter_identifier_like_node(
                    elem_node,
                    is_declarative=True,
                    is_on_lambda_str=is_on_lambda_str,
                    is_on_lambda_body=is_on_lambda_body,
                )
        else:
            self._enter_identifier_like_node(
                left_node,
                is_declarative=True,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        rest_node = node['rest']
        has_rest = type(rest_node) is not list
        if has_rest:
            self._enter_identifier_like_node(
                rest_node,
                is_declarative=True,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )


    def _enter_declarative_node(self, node, is_on_lambda_body, is_on_lambda_str):
        node_type = NodeType(node['type'])

        if node_type is NodeType.FUNCTION:
            self._enter_function_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        elif node_type is NodeType.LET:
            self._enter_let_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        elif node_type is NodeType.FOR:
            self._enter_for_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body
            )

        elif node_type is NodeType.EXCMD:
            self._enter_excmd_node(
                node,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )


    def _enter_call_node(self, call_node, is_on_lambda_body, is_on_lambda_str):
        called_func_node = call_node['left']
        self._enter_identifier_like_node(
            called_func_node,
            is_function=True,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
        )


    def _enter_string_node(self, string_node, is_on_lambda_body, is_on_lambda_str):
        # Classify the 2nd argument node of "map" and "filter" call when the node type is STRING.
        lambda_string_expr_content_nodes = get_lambda_string_expr_content(string_node)
        if lambda_string_expr_content_nodes is not None:
            self._enter_lambda_str_expr_content_node(
                lambda_string_expr_content_nodes,
                is_on_lambda_body=is_on_lambda_body
            )

        # Classify the 1st argument node of "call" and "function" call when the node type is STRING.
        func_ref_expr_content_nodes = get_function_reference_string_expr_content(string_node)
        if func_ref_expr_content_nodes is not None:
            self._enter_func_ref_str_expr_content_node(
                func_ref_expr_content_nodes,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body
            )

        return SKIP_CHILDREN


    def _enter_lambda_str_expr_content_node(self, lambda_string_expr_content_nodes, is_on_lambda_body):
        for string_expr_content_node in lambda_string_expr_content_nodes:
            traverse(
                string_expr_content_node,
                on_enter=lambda node: self._enter_handler(
                    node,
                    is_on_lambda_str=True,
                    is_on_lambda_body=is_on_lambda_body,
                )
            )


    def _enter_func_ref_str_expr_content_node(self, func_ref_id_nodes, is_on_lambda_str, is_on_lambda_body):
        for func_ref_id_node in func_ref_id_nodes:
            self._enter_identifier_terminate_node(
                func_ref_id_node,
                is_function=True,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body
            )


    def _enter_excmd_node(self, cmd_node, is_on_lambda_body, is_on_lambda_str):
        # Care an assignment by using command ":redir"
        redir_content_node = get_redir_content(cmd_node)

        if not redir_content_node:
            return

        self._enter_identifier_like_node(
            redir_content_node,
            is_on_lambda_str=is_on_lambda_str,
            is_on_lambda_body=is_on_lambda_body,
            is_declarative=True
        )


    def _enter_lambda_node(self, lambda_node, is_on_lambda_body, is_on_lambda_str):
        # Function parameter names are in the r_list.
        lambda_argument_nodes = lambda_node['rlist']

        for lambda_argument_node in lambda_argument_nodes:
            self._enter_identifier_terminate_node(
                lambda_argument_node,
                is_declarative=True,
                is_lambda_argument=True,
                is_on_lambda_str=is_on_lambda_str,
                is_on_lambda_body=is_on_lambda_body,
            )

        # Traversing on lambda body context.
        traverse(
            lambda_node['left'],
            on_enter=lambda node: self._enter_handler(
                node,
                is_on_lambda_body=True,
                is_on_lambda_str=is_on_lambda_str,
            )
        )

        # NOTE: Traversing to the lambda args and children was continued by the above traversing.
        return SKIP_CHILDREN

