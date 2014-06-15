var traverse = require('./ast/traverse.js').traverse;

function lint(policies, ast, env) {
  var listenersMap = {};
  policies.forEach(function(policy) {
    var listenedTypes = policy.listeningNodeType();

    listenedTypes.forEach(function(listenedType) {
      if (!(listenedType in listenersMap)) {
        listenersMap[listenedType] = [];
      }
      listenersMap[listenedType].push(policy);
    });
  });

  traverse(ast, function(node) {
    var listeners = listenersMap[node.type];
    if (!listeners) return;

    listeners.forEach(function(listener) {
      listener.handleNode(node, ast, env);
    })
  });

  var violations = [];
  policies.forEach(function(policy) {
    Array.prototype.push.apply(violations, policy.violations);
  });

  return violations;
}

exports.lint = lint;
