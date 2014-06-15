# coffeelint: disable=max_line_length
NodeType = require('./nodetype.js').NodeType

ChildNodePropertyStructure =
  NODE: (func, node) ->
    return if isNull(node)
    func(node)

  LIST: (func, nodes) ->
    for node in nodes
      func(node)

ChildType =
  LEFT:     { structure: ChildNodePropertyStructure.NODE, propertyName: 'left'     }
  RIGHT:    { structure: ChildNodePropertyStructure.NODE, propertyName: 'right'    }
  COND:     { structure: ChildNodePropertyStructure.NODE, propertyName: 'cond'     }
  REST:     { structure: ChildNodePropertyStructure.NODE, propertyName: 'rest'     }
  LIST:     { structure: ChildNodePropertyStructure.LIST, propertyName: 'list'     }
  RLIST:    { structure: ChildNodePropertyStructure.LIST, propertyName: 'rlist'    }
  BODY:     { structure: ChildNodePropertyStructure.LIST, propertyName: 'body'     }

  ELSEIF:   { structure: ChildNodePropertyStructure.LIST, propertyName: 'elseif'   }
  ELSE:     { structure: ChildNodePropertyStructure.NODE, propertyName: '_else'    }
  ENDIF:    { structure: ChildNodePropertyStructure.NODE, propertyName: 'endif'    }
  ENDWHILE: { structure: ChildNodePropertyStructure.NODE, propertyName: 'endwhile' }
  ENDFOR:   { structure: ChildNodePropertyStructure.NODE, propertyName: 'endfor'   }
  CATCH:    { structure: ChildNodePropertyStructure.LIST, propertyName: 'catch'    }
  FINALLY:  { structure: ChildNodePropertyStructure.NODE, propertyName: '_finally' }
  ENDTRY:   { structure: ChildNodePropertyStructure.NODE, propertyName: 'endtry'   }

ChildrenAccessorMap = {}
ChildrenAccessorMap[NodeType.TOPLEVEL]    = [ChildType.BODY]
ChildrenAccessorMap[NodeType.COMMENT]     = []
ChildrenAccessorMap[NodeType.EXCMD]       = []
ChildrenAccessorMap[NodeType.FUNCTION]    = [ChildType.BODY, ChildType.LEFT, ChildType.RLIST]
ChildrenAccessorMap[NodeType.ENDFUNCTION] = []
ChildrenAccessorMap[NodeType.DELFUNCTION] = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.RETURN]      = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.EXCALL]      = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.LET]         = [ChildType.LEFT, ChildType.LIST, ChildType.REST, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.UNLET]       = [ChildType.LIST]
ChildrenAccessorMap[NodeType.LOCKVAR]     = [ChildType.LIST]
ChildrenAccessorMap[NodeType.UNLOCKVAR]   = [ChildType.LIST]
ChildrenAccessorMap[NodeType.IF]          = [ChildType.BODY, ChildType.COND, ChildType.ELSEIF, ChildType.ELSE, ChildType.ENDIF]
ChildrenAccessorMap[NodeType.ELSEIF]      = [ChildType.BODY, ChildType.COND]
ChildrenAccessorMap[NodeType.ELSE]        = [ChildType.BODY]
ChildrenAccessorMap[NodeType.ENDIF]       = []
ChildrenAccessorMap[NodeType.WHILE]       = [ChildType.BODY, ChildType.COND, ChildType.ENDWHILE]
ChildrenAccessorMap[NodeType.ENDWHILE]    = []
ChildrenAccessorMap[NodeType.FOR]         = [ChildType.BODY, ChildType.LEFT, ChildType.LIST, ChildType.REST, ChildType.RIGHT, ChildType.ENDFOR]
ChildrenAccessorMap[NodeType.ENDFOR]      = []
ChildrenAccessorMap[NodeType.CONTINUE]    = []
ChildrenAccessorMap[NodeType.BREAK]       = []
ChildrenAccessorMap[NodeType.TRY]         = [ChildType.BODY, ChildType.CATCH, ChildType.FINALLY, ChildType.ENDTRY]
ChildrenAccessorMap[NodeType.CATCH]       = [ChildType.BODY]
ChildrenAccessorMap[NodeType.FINALLY]     = [ChildType.BODY]
ChildrenAccessorMap[NodeType.ENDTRY]      = []
ChildrenAccessorMap[NodeType.THROW]       = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.ECHO]        = [ChildType.LIST]
ChildrenAccessorMap[NodeType.ECHON]       = [ChildType.LIST]
ChildrenAccessorMap[NodeType.ECHOHL]      = []
ChildrenAccessorMap[NodeType.ECHOMSG]     = [ChildType.LIST]
ChildrenAccessorMap[NodeType.ECHOERR]     = [ChildType.LIST]
ChildrenAccessorMap[NodeType.EXECUTE]     = [ChildType.LIST]
ChildrenAccessorMap[NodeType.TERNARY]     = [ChildType.COND, ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.OR]          = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.AND]         = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.EQUAL]       = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.EQUALCI]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.EQUALCS]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NEQUAL]      = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NEQUALCI]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NEQUALCS]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.GREATER]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.GREATERCI]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.GREATERCS]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.GEQUAL]      = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.GEQUALCI]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.GEQUALCS]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SMALLER]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SMALLERCI]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SMALLERCS]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SEQUAL]      = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SEQUALCI]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SEQUALCS]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.MATCH]       = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.MATCHCI]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.MATCHCS]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NOMATCH]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NOMATCHCI]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NOMATCHCS]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.IS]          = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.ISCI]        = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.ISCS]        = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.ISNOT]       = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.ISNOTCI]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.ISNOTCS]     = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.ADD]         = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SUBTRACT]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.CONCAT]      = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.MULTIPLY]    = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.DIVIDE]      = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.REMAINDER]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NOT]         = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.MINUS]       = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.PLUS]        = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.SUBSCRIPT]   = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.SLICE]       = [ChildType.LEFT, ChildType.RLIST]
ChildrenAccessorMap[NodeType.CALL]        = [ChildType.LEFT, ChildType.RLIST]
ChildrenAccessorMap[NodeType.DOT]         = [ChildType.LEFT, ChildType.RIGHT]
ChildrenAccessorMap[NodeType.NUMBER]      = []
ChildrenAccessorMap[NodeType.STRING]      = []
ChildrenAccessorMap[NodeType.LIST]        = []
ChildrenAccessorMap[NodeType.DICT]        = []
ChildrenAccessorMap[NodeType.NESTING]     = [ChildType.LEFT]
ChildrenAccessorMap[NodeType.OPTION]      = []
ChildrenAccessorMap[NodeType.IDENTIFIER]  = []
ChildrenAccessorMap[NodeType.CURLYNAME]   = []
ChildrenAccessorMap[NodeType.ENV]         = []
ChildrenAccessorMap[NodeType.REG]         = []

traverse = (node, func) ->
  func(node)

  propertyAccessors = ChildrenAccessorMap[node.type]
  throw Error('Unknown node type: ' + node.type) if not propertyAccessors

  for propertyAccessor in propertyAccessors
    throw Error('Unknown child node property: ' + node.type) if not propertyAccessor

    propertyAccessor.structure((childNode) ->
      traverse(childNode, func)
    , node[propertyAccessor.propertyName])

isNull = (obj) -> obj.length == 0

module.exports =
  traverse: traverse
