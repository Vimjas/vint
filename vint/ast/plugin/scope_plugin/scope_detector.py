import enum
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG,
    IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG,
    IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG,
)
from vint.ast.plugin.scope_plugin.builtin_dictionary import (
    BuiltinVariables,
    BuiltinFunctions,
)


class ScopeVisibility(enum.Enum):
    """ 5 types scope visibility.
    We interest to analyze the variable scope by checking a single file.
    So, we do not interest to the strict visibility of the scopes that have a
    larger visibility than script local.
    """
    GLOBAL_LIKE = 0
    BUILTIN = 1
    SCRIPT_LOCAL = 2
    FUNCTION_LOCAL = 3
    UNANALYZABLE = 4


IdentifierScopePrefixToScopeVisibility = {
    'g:': ScopeVisibility.GLOBAL_LIKE,
    'b:': ScopeVisibility.GLOBAL_LIKE,
    'w:': ScopeVisibility.GLOBAL_LIKE,
    't:': ScopeVisibility.GLOBAL_LIKE,
    's:': ScopeVisibility.SCRIPT_LOCAL,
    'l:': ScopeVisibility.FUNCTION_LOCAL,
    'a:': ScopeVisibility.FUNCTION_LOCAL,
    'v:': ScopeVisibility.BUILTIN,
}


ImplicitScopeVisibilityToIdentifierScopePrefix = {
    ScopeVisibility.GLOBAL_LIKE: 'g:',
    ScopeVisibility.FUNCTION_LOCAL: 'l:',
    ScopeVisibility.BUILTIN: 'v:',
}


GlobalLikeScopeVisibilityNodeTypes = {
    NodeType.ENV: True,
    NodeType.OPTION: True,
    NodeType.REG: True,
}


IdentifierLikeNodeTypes = {
    NodeType.IDENTIFIER: True,
    NodeType.ENV: True,
    NodeType.OPTION: True,
    NodeType.REG: True,
}


class ScopeDetector(object):
    """ An utility namespace for variable visibility detection. """

    @classmethod
    def is_builtin_variable(cls, id_node):
        """ Whether the specified node is a builtin identifier. """
        is_identifier_like_node = IDENTIFIER_ATTRIBUTE in id_node
        if not is_identifier_like_node:
            return False

        id_value = id_node['value']
        if id_value.startswith('v:'):
            # It is an explicit builtin variable such as: "v:count", "v:char"
            # TODO: Add unknown builtin flag
            return True

        is_function = id_node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG]
        if is_function:
            # There are defference between a function identifier and variable
            # identifier:
            #
            #   let localtime = 0
            #   echo localtime " => 0
            #   echo localtime() " => 1420011455
            return id_value in BuiltinFunctions

        # It is an implicit builtin variable such as: "count", "char"
        return id_value in BuiltinVariables


    @classmethod
    def is_builtin_function(cls, id_node):
        """ Whether the specified node is a builtin function name identifier.
        The given identifier should be a child node of NodeType.CALL.
        """
        id_value = id_node['value']
        return id_value in BuiltinFunctions


    @classmethod
    def is_global_variable(cls, id_node, context_scope):
        """ Whether the specified node is a builtin identifier. """
        scope_visibility_hint = cls.detect_scope_visibility(id_node, context_scope)
        scope_visibility = scope_visibility_hint['scope_visibility']

        return scope_visibility in {
            ScopeVisibility.GLOBAL_LIKE: True,
            ScopeVisibility.BUILTIN: True,
        }


    @classmethod
    def is_analyzable_identifier(cls, node):
        """ Whether the specified node is an analyzable identifier.

        Node definition-identifier-like is analyzable if it is not dynamic
        and not a member variable, because we can do static scope analysis.

        Analyzable cases:
          - let s:var = 0
          - function! Func()
          - echo s:var

        Unanalyzable cases:
          - let s:my_{var} = 0
          - function! dict.Func()
          - echo s:my_{var}
        """
        is_identifier_like_node = IDENTIFIER_ATTRIBUTE in node

        if not is_identifier_like_node:
            return False

        id_attr = node[IDENTIFIER_ATTRIBUTE]
        return not (id_attr[IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG] or
                    id_attr[IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG])


    @classmethod
    def is_analyzable_definition_identifier(cls, node):
        """ Whether the specified node is an analyzable declarative identifier.
        Node definition-identifier-like is analyzable if it is not dynamic
        and not a member variable, because we can do static scope analysis.

        Analyzable cases:
          - let s:var = 0
          - function! Func()

        Unanalyzable cases:
          - let s:my_{var} = 0
          - function! dict.Func()
        """
        is_identifier_like_node = IDENTIFIER_ATTRIBUTE in node

        if not is_identifier_like_node:
            return False

        id_attr = node[IDENTIFIER_ATTRIBUTE]

        return id_attr[IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG] and \
            cls.is_analyzable_identifier(node)


    @classmethod
    def detect_scope_visibility(cls, node, context_scope):
        """ Returns a variable visibility hint by the specified node.
        The hint is a dict that has 2 attributes: "scope_visibility" and
        "is_implicit".
        """
        node_type = NodeType(node['type'])

        if not cls.is_analyzable_identifier(node):
            return cls._create_identifier_visibility_hint(ScopeVisibility.UNANALYZABLE)

        if node_type is NodeType.IDENTIFIER:
            return cls._detect_identifier_scope_visibility(node, context_scope)

        if node_type in GlobalLikeScopeVisibilityNodeTypes:
            return cls._create_identifier_visibility_hint(ScopeVisibility.GLOBAL_LIKE)


    @classmethod
    def normalize_variable_name(cls, node, context_scope):
        """ Returns normalized variable name.
        Normalizing means that variable names get explicit visibility by
        visibility prefix such as: "g:", "s:", ...

        Retunes None if the specified node is unanalyzable.
        A node is unanalyzable if:

        - the node is not identifier-like
        - the node is named dynamically
        """
        node_type = NodeType(node['type'])

        if not cls.is_analyzable_identifier(node):
            return None

        if node_type is NodeType.IDENTIFIER:
            return cls._normalize_identifier_value(node, context_scope)

        # Nodes identifier-like without identifier is always normalized because
        # the nodes can not have a visibility prefix.
        if node_type in IdentifierLikeNodeTypes:
            return node['value']


    @classmethod
    def normalize_parameter_name(cls, id_node):
        # param node is always NodeType.IDENTIFIER
        return 'a:' + id_node['value']


    @classmethod
    def _normalize_identifier_value(cls, id_node, context_scope):
        scope_visibility_hint = cls.detect_scope_visibility(id_node, context_scope)

        if not scope_visibility_hint['is_implicit']:
            return id_node['value']

        scope_visibility = scope_visibility_hint['scope_visibility']
        scope_prefix = ImplicitScopeVisibilityToIdentifierScopePrefix[scope_visibility]

        return scope_prefix + id_node['value']


    @classmethod
    def _detect_identifier_scope_visibility(cls, id_node, context_scope):
        id_value = id_node['value']

        explicit_scope_visibility = cls._get_explicit_scope_visibility(id_value)
        if explicit_scope_visibility is not None:
            return cls._create_identifier_visibility_hint(explicit_scope_visibility)

        # Implicit scope variable will be resolved as a builtin variable if it
        # has a same name to Vim builtin variables.
        if cls.is_builtin_variable(id_node):
            return cls._create_identifier_visibility_hint(ScopeVisibility.BUILTIN,
                                                          is_implicit=True)

        current_scope_visibility = context_scope['scope_visibility']

        # Implicit scope variable will be resolved as a global variable when
        # current scope is script local. Otherwise be a function local variable.
        if current_scope_visibility is ScopeVisibility.SCRIPT_LOCAL:
            return cls._create_identifier_visibility_hint(ScopeVisibility.GLOBAL_LIKE,
                                                          is_implicit=True)

        return cls._create_identifier_visibility_hint(ScopeVisibility.FUNCTION_LOCAL,
                                                      is_implicit=True)


    @classmethod
    def _get_explicit_scope_visibility(cls, id_value):
        # See :help internal-variables
        scope_prefix = id_value[0:2]
        return IdentifierScopePrefixToScopeVisibility.get(scope_prefix, None)


    @classmethod
    def _create_identifier_visibility_hint(cls, visibility, is_implicit=False):
        return {
            'scope_visibility': visibility,
            'is_implicit': is_implicit,
        }
