from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.identifier_attribute import (
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG,
    IDENTIFIER_ATTRIBUTE_MEMBER_FLAG,
    IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG,
    IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG,
    IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG,
    IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT,
)


def create_id(id_value, is_declarative=True, is_function=False, is_autoload=False,
              is_declarative_parameter=False, is_on_str_expr_context=False):
    return {
        'type': NodeType.IDENTIFIER.value,
        'value': id_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: is_declarative,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: is_function,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: is_autoload,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: is_declarative_parameter,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: is_on_str_expr_context,
        },
    }


def create_env(env_value):
    return {
        'type': NodeType.ENV.value,
        'value': env_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: False,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: False,
        },
    }


def create_option(opt_value):
    return {
        'type': NodeType.OPTION.value,
        'value': opt_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: False,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: False,
        },
    }


def create_reg(reg_value):
    return {
        'type': NodeType.REG.value,
        'value': reg_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: False,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: False,
        },
    }


def create_curlyname(is_declarative=True):
    """ Create a node as a `my_{'var'}`
    """
    return {
        'type': NodeType.CURLYNAME.value,
        'value': [
            {
                'type': NodeType.CURLYNAMEPART.value,
                'value': 'my_',
            },
            {
                'type': NodeType.CURLYNAMEEXPR.value,
                'value': {
                    'type': NodeType.CURLYNAMEEXPR.value,
                    'value': 'var',
                },
            }
        ],
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: is_declarative,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: True,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: False,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: False,
        },
    }


def create_subscript_member(is_declarative=True):
    return {
        'type': NodeType.IDENTIFIER.value,
        'value': 'member',
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: is_declarative,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: True,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: False,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: False,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: False,
        },
    }
