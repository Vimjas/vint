import pytest
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG,
    IDENTIFIER_ATTRIBUTE_MEMBER_FLAG,
    IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG,
    IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG,
    IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG,
)
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeVisibility as Vis,
    detect_scope_visibility,
    normalize_variable_name,
    is_builtin_variable,
    ExplicityOfScopeVisibility,
    get_explicity_of_scope_visibility,
)


def create_scope(visibility):
    return {
        'scope_visibility': visibility,
    }


def create_scope_visibility_hint(visibility, is_implicit=False):
    return {
        'scope_visibility': visibility,
        'is_implicit': is_implicit,
    }


def create_id(id_value, is_declarative=True, is_function=False, is_autoload=False,
              is_declarative_parameter=False):
    return {
        'type': NodeType.IDENTIFIER.value,
        'value': id_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: is_declarative,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: False,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: is_function,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: is_autoload,
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: is_declarative_parameter,
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
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: False,
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
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: False,
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
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: False,
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
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: False,
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
            IDENTIFIER_ATTRIBUTE_PARAMETER_DECLARATION_FLAG: False,
        },
    }


@pytest.mark.parametrize(
    'context_scope_visibility, id_node, expected_scope_visibility, expected_implicity', [
        # Declarative variable test
        (Vis.SCRIPT_LOCAL, create_id('g:explicit_global'), Vis.GLOBAL_LIKE, False),
        (Vis.SCRIPT_LOCAL, create_id('implicit_global'), Vis.GLOBAL_LIKE, True),
        (Vis.FUNCTION_LOCAL, create_id('g:explicit_global'), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('b:buffer_local'), Vis.GLOBAL_LIKE, False),
        (Vis.FUNCTION_LOCAL, create_id('b:buffer_local'), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('w:window_local'), Vis.GLOBAL_LIKE, False),
        (Vis.FUNCTION_LOCAL, create_id('w:window_local'), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('s:script_local'), Vis.SCRIPT_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('s:script_local'), Vis.SCRIPT_LOCAL, False),

        (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local'), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('implicit_function_local'), Vis.FUNCTION_LOCAL, True),

        (Vis.FUNCTION_LOCAL, create_id('a:param'), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:000'), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:1'), Vis.FUNCTION_LOCAL, False),

        (Vis.SCRIPT_LOCAL, create_id('v:count'), Vis.BUILTIN, False),
        (Vis.FUNCTION_LOCAL, create_id('v:count'), Vis.BUILTIN, False),
        (Vis.FUNCTION_LOCAL, create_id('count'), Vis.BUILTIN, True),

        (Vis.SCRIPT_LOCAL, create_curlyname(), Vis.UNANALYZABLE, False),
        (Vis.FUNCTION_LOCAL, create_curlyname(), Vis.UNANALYZABLE, False),

        (Vis.SCRIPT_LOCAL, create_subscript_member(), Vis.UNANALYZABLE, False),
        (Vis.FUNCTION_LOCAL, create_subscript_member(), Vis.UNANALYZABLE, False),

        # Referencing variable test
        (Vis.SCRIPT_LOCAL, create_id('g:explicit_global', is_declarative=False), Vis.GLOBAL_LIKE, False),
        (Vis.SCRIPT_LOCAL, create_id('implicit_global', is_declarative=False), Vis.GLOBAL_LIKE, True),
        (Vis.FUNCTION_LOCAL, create_id('g:explicit_global', is_declarative=False), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('b:buffer_local', is_declarative=False), Vis.GLOBAL_LIKE, False),
        (Vis.FUNCTION_LOCAL, create_id('b:buffer_local', is_declarative=False), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('w:window_local', is_declarative=False), Vis.GLOBAL_LIKE, False),
        (Vis.FUNCTION_LOCAL, create_id('w:window_local', is_declarative=False), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('s:script_local', is_declarative=False), Vis.SCRIPT_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('s:script_local', is_declarative=False), Vis.SCRIPT_LOCAL, False),

        (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local', is_declarative=False), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('implicit_function_local', is_declarative=False), Vis.FUNCTION_LOCAL, True),

        (Vis.FUNCTION_LOCAL, create_id('param', is_declarative=False, is_declarative_parameter=True), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:param', is_declarative=False), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:000', is_declarative=False), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:1', is_declarative=False), Vis.FUNCTION_LOCAL, False),

        (Vis.SCRIPT_LOCAL, create_id('v:count', is_declarative=False), Vis.BUILTIN, False),
        (Vis.FUNCTION_LOCAL, create_id('v:count', is_declarative=False), Vis.BUILTIN, False),
        (Vis.FUNCTION_LOCAL, create_id('count', is_declarative=False), Vis.BUILTIN, True),

        (Vis.SCRIPT_LOCAL, create_curlyname(is_declarative=False), Vis.UNANALYZABLE, False),
        (Vis.FUNCTION_LOCAL, create_curlyname(is_declarative=False), Vis.UNANALYZABLE, False),

        (Vis.SCRIPT_LOCAL, create_subscript_member(is_declarative=False), Vis.UNANALYZABLE, False),
        (Vis.FUNCTION_LOCAL, create_subscript_member(is_declarative=False), Vis.UNANALYZABLE, False),

        (Vis.FUNCTION_LOCAL, create_id('file#func', is_autoload=True, is_function=True, is_declarative=False), Vis.GLOBAL_LIKE, True),
    ]
)
def test_detect_scope_visibility(context_scope_visibility, id_node, expected_scope_visibility, expected_implicity):
    scope = create_scope(context_scope_visibility)
    scope_visibility_hint = detect_scope_visibility(id_node, scope)

    expected_scope_visibility_hint = create_scope_visibility_hint(expected_scope_visibility,
                                                                  is_implicit=expected_implicity)
    assert expected_scope_visibility_hint == scope_visibility_hint



@pytest.mark.parametrize(
    'context_scope_visibility, node, expected_variable_name', [
        (Vis.SCRIPT_LOCAL, create_id('g:explicit_global'), 'g:explicit_global'),
        (Vis.SCRIPT_LOCAL, create_id('implicit_global'), 'g:implicit_global'),
        (Vis.SCRIPT_LOCAL, create_id('implicit_global', is_declarative=False), 'g:implicit_global'),

        (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local'), 'l:explicit_function_local'),
        (Vis.FUNCTION_LOCAL, create_id('implicit_function_local'), 'l:implicit_function_local'),
        (Vis.FUNCTION_LOCAL, create_id('implicit_function_local', is_declarative=False), 'l:implicit_function_local'),

        (Vis.FUNCTION_LOCAL, create_id('param', is_declarative=False, is_declarative_parameter=True), 'param'),

        (Vis.SCRIPT_LOCAL, create_id('v:count'), 'v:count'),
        (Vis.FUNCTION_LOCAL, create_id('v:count'), 'v:count'),
        (Vis.FUNCTION_LOCAL, create_id('count'), 'v:count'),

        (Vis.SCRIPT_LOCAL, create_env('$ENV'), '$ENV'),
        (Vis.SCRIPT_LOCAL, create_option('&OPT'), '&OPT'),
        (Vis.SCRIPT_LOCAL, create_reg('@"'), '@"'),
    ]
)
def test_normalize_variable_name(context_scope_visibility, node, expected_variable_name):
    scope = create_scope(context_scope_visibility)
    normalized_variable_name = normalize_variable_name(node, scope)

    assert expected_variable_name == normalized_variable_name



@pytest.mark.parametrize(
    'id_value, is_function, expected_result', [
        ('my_var', False, False),
        ('count', False, True),
        ('v:count', False, True),

        ('MyFunc', True, False),
        ('localtime', True, True),
    ]
)
def test_is_builtin_variable(id_value, is_function, expected_result):
    id_node = create_id(id_value, is_function=is_function)
    result = is_builtin_variable(id_node)

    assert expected_result == result



@pytest.mark.parametrize(
    'node, expected_result', [
        (create_id('my_var'), ExplicityOfScopeVisibility.IMPLICIT),
        (create_id('g:my_var'), ExplicityOfScopeVisibility.EXPLICIT),
        (create_id('param', is_declarative=True, is_declarative_parameter=True), ExplicityOfScopeVisibility.EXPLICIT),
        (create_curlyname(), ExplicityOfScopeVisibility.UNANALYZABLE),
    ]
)
def test_get_explicity_of_scope_visibility(node, expected_result):
    result = get_explicity_of_scope_visibility(node)
    assert expected_result == result
