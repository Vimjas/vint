from typing import Dict, Any, Optional


IDENTIFIER_ATTRIBUTE = 'VINT:identifier_attribute'
IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG = 'is_declarative'
IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG = 'is_dynamic'
IDENTIFIER_ATTRIBUTE_MEMBER_FLAG = 'is_member'
IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG = 'is_function'
IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG = 'is_autoload'
IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG = 'is_function_argument'
IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT = 'is_on_lambda_string_context'
IDENTIFIER_ATTRIBUTE_VARIADIC_SYMBOL_FLAG = 'is_variadic_symbol'
IDENTIFIER_ATTRIBUTE_LAMBDA_ARGUMENT_FLAG = 'is_lambda_argument'
IDENTIFIER_ATTRIBUTE_LAMBDA_BODY_CONTEXT = 'is_on_lambda_body'


def is_identifier_like_node(node): # type: (Dict[str, Any]) -> bool
    return IDENTIFIER_ATTRIBUTE in node


def is_function_identifier(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG]


def is_dynamic_identifier(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG]


def is_declarative_identifier(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG]


def is_member_identifier(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_MEMBER_FLAG]


def is_autoload_identifier(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG]


def is_function_argument(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG]


def is_on_lambda_string_context(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT]


def is_variadic_symbol(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_VARIADIC_SYMBOL_FLAG]


def is_lambda_argument_identifier(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_LAMBDA_ARGUMENT_FLAG]


def is_on_lambda_body_context(node): # type: (Dict[str, Any]) -> bool
    if not is_identifier_like_node(node):
        return False

    return node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_LAMBDA_BODY_CONTEXT]


# FIXME: Fix the shit function signature. But be careful about multiple identifier attribute setting.
def set_identifier_attribute(node, is_on_lambda_body, is_on_lambda_str, is_declarative=None, is_dynamic=None, is_member=None, is_function=None, is_autoload=None,
        is_declarative_parameter=None, is_variadic=None, is_lambda_argument=None):
    # type: (Dict[str, Any], Optional[bool], Optional[bool], Optional[bool], Optional[bool], Optional[bool], Optional[bool], Optional[bool], Optional[bool], Optional[bool], Optional[bool]) -> None
    id_attr = node.setdefault(IDENTIFIER_ATTRIBUTE, {
        IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: False,
        IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
        IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
        IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
        IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
        IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: False,
        IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: False,
        IDENTIFIER_ATTRIBUTE_VARIADIC_SYMBOL_FLAG: False,
        IDENTIFIER_ATTRIBUTE_LAMBDA_ARGUMENT_FLAG: False,
        IDENTIFIER_ATTRIBUTE_LAMBDA_BODY_CONTEXT: False
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
        id_attr[IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG] = is_declarative_parameter

    if is_on_lambda_str is not None:
        id_attr[IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT] = is_on_lambda_str

    if is_variadic is not None:
        id_attr[IDENTIFIER_ATTRIBUTE_VARIADIC_SYMBOL_FLAG] = is_variadic

    if is_lambda_argument is not None:
        id_attr[IDENTIFIER_ATTRIBUTE_LAMBDA_ARGUMENT_FLAG] = is_lambda_argument

    if is_on_lambda_body is not None:
        id_attr[IDENTIFIER_ATTRIBUTE_LAMBDA_BODY_CONTEXT] = is_on_lambda_body
