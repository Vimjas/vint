traverse = require('./ast/traverse.coffee').traverse

lint = (policies, ast, env) ->
  listenersMap = {}
  for policy in policies
    for listenedType in policy.listeningNodeType()
      if listenedType not in listenersMap
        listenersMap[listenedType] = []
      listenersMap[listenedType].push(policy)

  traverse(ast, (node) ->
    listeners = listenersMap[node.type]
    return if not listeners

    for listener in listeners
      listener.handleNode(node, ast, env))

  violations = []
  for policy in policies
    Array.prototype.push.apply(violations, policy.violations)

  return violations

exports.lint = lint
