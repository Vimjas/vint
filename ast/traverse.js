var NodeType = require('./nodetype.js').NodeType;

var ChildNodePropertyStructure = {
  NODE: function(func, node) {
    if (isNull(node)) return;
    func(node);
  },
  LIST: function(func, nodes) {
    nodes.forEach(func);
  },
};

var ChildNodePropertyType = {
  LEFT     : { structure: ChildNodePropertyStructure.NODE, propertyName: 'left' },
  RIGHT    : { structure: ChildNodePropertyStructure.NODE, propertyName: 'right' },
  COND     : { structure: ChildNodePropertyStructure.NODE, propertyName: 'cond' },
  REST     : { structure: ChildNodePropertyStructure.NODE, propertyName: 'rest' },
  LIST     : { structure: ChildNodePropertyStructure.LIST, propertyName: 'list' },
  RLIST    : { structure: ChildNodePropertyStructure.LIST, propertyName: 'rlist' },
  BODY     : { structure: ChildNodePropertyStructure.LIST, propertyName: 'body' },

  ELSEIF   : { structure: ChildNodePropertyStructure.LIST, propertyName: 'elseif' },
  ELSE     : { structure: ChildNodePropertyStructure.NODE, propertyName: '_else' },
  ENDIF    : { structure: ChildNodePropertyStructure.NODE, propertyName: 'endif' },
  ENDWHILE : { structure: ChildNodePropertyStructure.NODE, propertyName: 'endwhile' },
  ENDFOR   : { structure: ChildNodePropertyStructure.NODE, propertyName: 'endfor' },
  CATCH    : { structure: ChildNodePropertyStructure.LIST, propertyName: 'catch' },
  FINALLY  : { structure: ChildNodePropertyStructure.NODE, propertyName: '_finally' },
  ENDTRY   : { structure: ChildNodePropertyStructure.NODE, propertyName: 'endtry' },
};

var ChildNodePropertyAccessorMap = {};
ChildNodePropertyAccessorMap[NodeType.TOPLEVEL]    = [ChildNodePropertyType.BODY];
ChildNodePropertyAccessorMap[NodeType.COMMENT]     = [];
ChildNodePropertyAccessorMap[NodeType.EXCMD]       = [];
ChildNodePropertyAccessorMap[NodeType.FUNCTION]    = [ChildNodePropertyType.BODY, ChildNodePropertyType.LEFT, ChildNodePropertyType.RLIST];
ChildNodePropertyAccessorMap[NodeType.ENDFUNCTION] = [];
ChildNodePropertyAccessorMap[NodeType.DELFUNCTION] = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.RETURN]      = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.EXCALL]      = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.LET]         = [ChildNodePropertyType.LEFT, ChildNodePropertyType.LIST, ChildNodePropertyType.REST, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.UNLET]       = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.LOCKVAR]     = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.UNLOCKVAR]   = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.IF]          = [ChildNodePropertyType.BODY, ChildNodePropertyType.COND, ChildNodePropertyType.ELSEIF, ChildNodePropertyType.ELSE, ChildNodePropertyType.ENDIF];
ChildNodePropertyAccessorMap[NodeType.ELSEIF]      = [ChildNodePropertyType.BODY, ChildNodePropertyType.COND];
ChildNodePropertyAccessorMap[NodeType.ELSE]        = [ChildNodePropertyType.BODY];
ChildNodePropertyAccessorMap[NodeType.ENDIF]       = [];
ChildNodePropertyAccessorMap[NodeType.WHILE]       = [ChildNodePropertyType.BODY, ChildNodePropertyType.COND, ChildNodePropertyType.ENDWHILE];
ChildNodePropertyAccessorMap[NodeType.ENDWHILE]    = [];
ChildNodePropertyAccessorMap[NodeType.FOR]         = [ChildNodePropertyType.BODY, ChildNodePropertyType.LEFT, ChildNodePropertyType.LIST, ChildNodePropertyType.REST, ChildNodePropertyType.RIGHT, ChildNodePropertyType.ENDFOR];
ChildNodePropertyAccessorMap[NodeType.ENDFOR]      = [];
ChildNodePropertyAccessorMap[NodeType.CONTINUE]    = [];
ChildNodePropertyAccessorMap[NodeType.BREAK]       = [];
ChildNodePropertyAccessorMap[NodeType.TRY]         = [ChildNodePropertyType.BODY, ChildNodePropertyType.CATCH, ChildNodePropertyType.FINALLY, ChildNodePropertyType.ENDTRY];
ChildNodePropertyAccessorMap[NodeType.CATCH]       = [ChildNodePropertyType.BODY];
ChildNodePropertyAccessorMap[NodeType.FINALLY]     = [ChildNodePropertyType.BODY];
ChildNodePropertyAccessorMap[NodeType.ENDTRY]      = [];
ChildNodePropertyAccessorMap[NodeType.THROW]       = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.ECHO]        = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.ECHON]       = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.ECHOHL]      = [];
ChildNodePropertyAccessorMap[NodeType.ECHOMSG]     = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.ECHOERR]     = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.EXECUTE]     = [ChildNodePropertyType.LIST];
ChildNodePropertyAccessorMap[NodeType.TERNARY]     = [ChildNodePropertyType.COND, ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.OR]          = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.AND]         = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.EQUAL]       = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.EQUALCI]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.EQUALCS]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NEQUAL]      = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NEQUALCI]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NEQUALCS]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.GREATER]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.GREATERCI]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.GREATERCS]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.GEQUAL]      = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.GEQUALCI]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.GEQUALCS]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SMALLER]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SMALLERCI]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SMALLERCS]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SEQUAL]      = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SEQUALCI]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SEQUALCS]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.MATCH]       = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.MATCHCI]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.MATCHCS]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NOMATCH]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NOMATCHCI]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NOMATCHCS]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.IS]          = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.ISCI]        = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.ISCS]        = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.ISNOT]       = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.ISNOTCI]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.ISNOTCS]     = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.ADD]         = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SUBTRACT]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.CONCAT]      = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.MULTIPLY]    = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.DIVIDE]      = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.REMAINDER]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NOT]         = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.MINUS]       = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.PLUS]        = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.SUBSCRIPT]   = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.SLICE]       = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RLIST];
ChildNodePropertyAccessorMap[NodeType.CALL]        = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RLIST];
ChildNodePropertyAccessorMap[NodeType.DOT]         = [ChildNodePropertyType.LEFT, ChildNodePropertyType.RIGHT];
ChildNodePropertyAccessorMap[NodeType.NUMBER]      = [];
ChildNodePropertyAccessorMap[NodeType.STRING]      = [];
ChildNodePropertyAccessorMap[NodeType.LIST]        = [];
ChildNodePropertyAccessorMap[NodeType.DICT]        = [];
ChildNodePropertyAccessorMap[NodeType.NESTING]     = [ChildNodePropertyType.LEFT];
ChildNodePropertyAccessorMap[NodeType.OPTION]      = [];
ChildNodePropertyAccessorMap[NodeType.IDENTIFIER]  = [];
ChildNodePropertyAccessorMap[NodeType.CURLYNAME]   = [];
ChildNodePropertyAccessorMap[NodeType.ENV]         = [];
ChildNodePropertyAccessorMap[NodeType.REG]         = [];

function traverse(node, func) {
  func(node);

  var propertyAccessors = ChildNodePropertyAccessorMap[node.type];
  if (!propertyAccessors) throw Error('Unknown node type: ' + node.type);

  propertyAccessors.forEach(function(propertyAccessor) {
    if (!propertyAccessor) throw Error('Unknown child node property: ' + node.type);
    propertyAccessor.structure(function(childNode) {
      traverse(childNode, func);
    }, node[propertyAccessor.propertyName]);
  });
};

function isNull(obj) {
  return obj.length === 0;
}

module.exports = {
  traverse: traverse,
};
