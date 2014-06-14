var inherits = require('util').inherits;
var Policy = require('./policy.js');
var NodeType = require('../ast/nodetype.js').NodeType;



/**
 * A class for validation policy of double quoted string.
 * @param {number} violationId Violation ID.
 * @constructor
 * @extends {Policy}
 */
function ProhibitUnnecessaryDoubleQuote(violationId) {
  Policy.call(this, violationId);
  this.desc = 'Prefer single quoted strings.';
  this.name = 'ProhibitUnnecessaryDoubleQuote';
  this.ref = 'Google VimScript Style Guide #Strings';
};
inherits(ProhibitUnnecessaryDoubleQuote, Policy);


/** @override */
ProhibitUnnecessaryDoubleQuote.prototype.listeningNodeType = function() {
  var listeningNodeType = Policy.prototype.listeningNodeType.call(this);

  listeningNodeType.push(NodeType.STRING);
  return listeningNodeType;
};


/** @override */
ProhibitUnnecessaryDoubleQuote.prototype.isValid = function(node, root) {
  var isDoubleQuoted = node.value[0] !== '"';
  if (!isDoubleQuoted) return false;

  return Boolean(STRING_SPECIAL_CHAR_MATCHER.test(node.value));
};


/**
 * Special character mathcer for string constants.
 * @const
 * @type {RegExp}
 * @see `:help expr-string`
 */
var STRING_SPECIAL_CHAR_MATCHER = (function buildSpecialCharMathcer() {
  var StringConstantSpecialChar = {
    OCTAL                       : '[0-7]{1,3}',
    HEXADECIMAL                 : '[xX][0-9a-fA-F]{1,2}',
    NUMERIC_CHARACTER_REFERENCE : '[uU][0-9a-fA-F]{4}',
    BACKSPACE                   : 'b',
    ESCAPE                      : 'e',
    FORM_FEED                   : 'f',
    NEW_LINE                    : 'n',
    CARRIAGE_RETURN             : 'r',
    TAB                         : 't',
    BACKSLASH                   : '\\\\',
    DOUBLE_QUPTE                : '"',
    SPECIAL_KEY                 : '<[^>]+>',
  };

  var subRegExps = Object.keys(StringConstantSpecialChar).map(function(key) {
    return StringConstantSpecialChar[key];
  });

  return RegExp('\\\\(' + subRegExps.join('|') + ')');
})();

module.exports = ProhibitUnnecessaryDoubleQuote;
