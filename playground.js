var VimLParser = require('./vimlparser.js');
var fs = require('fs');
var Reporter = require('./reporter/reporter.js');

var parser = new VimLParser.VimLParser();

var filepath = '/Users/OrgaChem/.vimrc';

fs.readFile(filepath, 'utf-8', function(err, content) {
  if (err) {
    throw err;
  }

  var lines = content.split(/\r\n|\r|\n/);
  var stringReader = new VimLParser.StringReader(lines);
  var ast = parser.parse(stringReader);

  var violationId = 0;
  var listenersMap = {};

  var policies = policiesCtor.map(function (PolicyCtor) {
    var policy = new PolicyCtor(violationId++);
    attachASTListeners(policy, listenersMap);
    return policy;
  });

  var traverse = require('./ast/traverse.js').traverse;

  traverse(ast, function(node) {
    var listeners = listenersMap[node.type];
    if (!listeners) return;

    listeners.forEach(function(listener) {
      listener.handleNode(node, ast, filepath);
    })
  });

  report(policies);
});

var policiesCtor = [
  require('./policy/prohibit_unnecessary_double_quote.js'),
];


function attachASTListeners(policy, listenersMap) {
  var listenedTypes = policy.listeningNodeType();

  listenedTypes.forEach(function(listenedType) {
    if (!(listenedType in listenersMap)) {
      listenersMap[listenedType] = [];
    }
    listenersMap[listenedType].push(policy);
  });
}


function report(policies) {
  var reporter = new Reporter();
  var violations = [];
  policies.forEach(function(policy) {
    Array.prototype.push.apply(violations, policy.violations);
  });
  console.log(reporter.formatAll(violations));
}
