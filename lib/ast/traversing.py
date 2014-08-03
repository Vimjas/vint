from lib.ast.nodetype import NodeType
from lib.ast.nodetype import get_node_type_name


ChildNodeAccessor = {
    'NODE': lambda func, node: call_if_def(func, node),
    'LIST': lambda func, nodes: for_each(func, nodes),
}

ChildType = {
    'LEFT': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'left',
    },
    'RIGHT': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'right',
    },
    'COND': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'cond',
    },
    'REST': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'rest',
    },
    'LIST': {
        'accessor': ChildNodeAccessor['LIST'],
        'property_name': 'list',
    },
    'RLIST': {
        'accessor': ChildNodeAccessor['LIST'],
        'property_name': 'rlist',
    },
    'BODY': {
        'accessor': ChildNodeAccessor['LIST'],
        'property_name': 'body',
    },

    'ELSEIF': {
        'accessor': ChildNodeAccessor['LIST'],
        'property_name': 'elseif',
    },
    'ELSE': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': '_else',
    },
    'ENDIF': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'endif',
    },
    'ENDWHILE': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'endwhile',
    },
    'ENDFOR': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'endfor',
    },
    'CATCH': {
        'accessor': ChildNodeAccessor['LIST'],
        'property_name': 'catch',
    },
    'FINALLY': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': '_finally',
    },
    'ENDTRY': {
        'accessor': ChildNodeAccessor['NODE'],
        'property_name': 'endtry',
    },
}

ChildNodeAccessorMap = {
    NodeType['TOPLEVEL']: [ChildType['BODY']],
    NodeType['COMMENT']: [],
    NodeType['EXCMD']: [],
    NodeType['FUNCTION']: [ChildType['BODY'], ChildType['LEFT'], ChildType['RLIST']],
    NodeType['ENDFUNCTION']: [],
    NodeType['DELFUNCTION']: [ChildType['LEFT']],
    NodeType['RETURN']: [ChildType['LEFT']],
    NodeType['EXCALL']: [ChildType['LEFT']],
    NodeType['LET']: [ChildType['LEFT'], ChildType['LIST'], ChildType['REST'], ChildType['RIGHT']],
    NodeType['UNLET']: [ChildType['LIST']],
    NodeType['LOCKVAR']: [ChildType['LIST']],
    NodeType['UNLOCKVAR']: [ChildType['LIST']],
    NodeType['IF']: [ChildType['BODY'], ChildType['COND'], ChildType['ELSEIF'], ChildType['ELSE'], ChildType['ENDIF']],
    NodeType['ELSEIF']: [ChildType['BODY'], ChildType['COND']],
    NodeType['ELSE']: [ChildType['BODY']],
    NodeType['ENDIF']: [],
    NodeType['WHILE']: [ChildType['BODY'], ChildType['COND'], ChildType['ENDWHILE']],
    NodeType['ENDWHILE']: [],
    NodeType['FOR']: [ChildType['BODY'], ChildType['LEFT'], ChildType['LIST'], ChildType['REST'], ChildType['RIGHT'], ChildType['ENDFOR']],
    NodeType['ENDFOR']: [],
    NodeType['CONTINUE']: [],
    NodeType['BREAK']: [],
    NodeType['TRY']: [ChildType['BODY'], ChildType['CATCH'], ChildType['FINALLY'], ChildType['ENDTRY']],
    NodeType['CATCH']: [ChildType['BODY']],
    NodeType['FINALLY']: [ChildType['BODY']],
    NodeType['ENDTRY']: [],
    NodeType['THROW']: [ChildType['LEFT']],
    NodeType['ECHO']: [ChildType['LIST']],
    NodeType['ECHON']: [ChildType['LIST']],
    NodeType['ECHOHL']: [],
    NodeType['ECHOMSG']: [ChildType['LIST']],
    NodeType['ECHOERR']: [ChildType['LIST']],
    NodeType['EXECUTE']: [ChildType['LIST']],
    NodeType['TERNARY']: [ChildType['COND'], ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['OR']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['AND']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['EQUAL']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['EQUALCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['EQUALCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NEQUAL']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NEQUALCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NEQUALCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['GREATER']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['GREATERCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['GREATERCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['GEQUAL']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['GEQUALCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['GEQUALCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SMALLER']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SMALLERCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SMALLERCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SEQUAL']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SEQUALCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SEQUALCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['MATCH']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['MATCHCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['MATCHCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NOMATCH']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NOMATCHCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NOMATCHCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['IS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['ISCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['ISCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['ISNOT']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['ISNOTCI']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['ISNOTCS']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['ADD']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SUBTRACT']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['CONCAT']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['MULTIPLY']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['DIVIDE']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['REMAINDER']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NOT']: [ChildType['LEFT']],
    NodeType['MINUS']: [ChildType['LEFT']],
    NodeType['PLUS']: [ChildType['LEFT']],
    NodeType['SUBSCRIPT']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['SLICE']: [ChildType['LEFT'], ChildType['RLIST']],
    NodeType['CALL']: [ChildType['LEFT'], ChildType['RLIST']],
    NodeType['DOT']: [ChildType['LEFT'], ChildType['RIGHT']],
    NodeType['NUMBER']: [],
    NodeType['STRING']: [],
    NodeType['LIST']: [],
    NodeType['DICT']: [],
    NodeType['NESTING']: [ChildType['LEFT']],
    NodeType['OPTION']: [],
    NodeType['IDENTIFIER']: [],
    NodeType['CURLYNAME']: [],
    NodeType['ENV']: [],
    NodeType['REG']: [],
}


class UnknownNodeTypeException(BaseException):
    def __init__(self, node_type):
        self.node_type = node_type

    def __str__(self):
        node_type_name = get_node_type_name(self.node_type)
        return 'Unknown node type: `{node_type}`'.format(node_type=node_type_name)


def for_each(func, nodes):
    """ Calls func for each the specified nodes. """
    for node in nodes:
        func(node)


def call_if_def(func, node):
    """ Calls func if the node is defined.
    VimLParser return an empty array if a child node is not defined.
    """
    if hasattr(node, 'type'):
        func(node)


def traverse(func, node):
    """ Traverses the specified Vim script AST node (depth first order).
    The func will be called the specified node and the children.
    """
    node_type = node['type']

    if node_type not in ChildNodeAccessorMap:
        raise UnknownNodeTypeException(node_type)

    func(node)

    for property_accessor in ChildNodeAccessorMap[node_type]:
        accessor_func = property_accessor['accessor']
        prop_name = property_accessor['property_name']

        accessor_func(lambda child_node: traverse(func, child_node), node[prop_name])
