/**
 * Source code position.
 * @typedef {{ i: number, lnum: number, col: number, path: string, ref: string }}
 */
var Position;


/**
 * Violation object to report.
 * @typedef {{ id: number, pos: Position, desc: string }}
 */
var Violation;


/**
 * A class for abstract validation policy.
 * @param {number} violationId Violation ID.
 * @constructor
 */
function Policy(violationId) {
  this.violations = [];
  this.violationId = violationId;
  this.name = null;
  this.desc = null;
  this.ref = null;
};


/**
 * Returns a listening node type.
 * @return {Array.<NodeType>} Node type to listen.
 */
Policy.prototype.listeningNodeType = function() {
  return [];
};


/**
 * Handles the specified node.
 * In default, store a violation object if the node has any violations.
 * @param {Node} node Vim language AST node to check.
 * @param {Node} root Root Vim language AST node.
 * @param {string} path File path ot the AST.
 */
Policy.prototype.handleNode = function(node, root, path) {
  var isValidNode = this.isValid(node, root);
  if (!isValidNode) {
    this.violations.push(this.createViolationReport(node.pos, path, node));
  }
};


/**
 * Creates a violation report.
 * @param {Position} pos Violation position.
 * @param {string} path File path ot the AST.
 * @return {Violation} Violation object.
 * @protected
 */
Policy.prototype.createViolationReport = function(pos, path) {
  return {
    id: this.violationId,
    desc: this.desc,
    ref: this.ref,
    path: path,
    pos: pos,
  };
};


/**
 * Returns whether the specified node is valid to the policy.
 * @param {Node} node Vim language AST node to check.
 * @param {Node} root Root Vim language AST node.
 * @return {Boolean} Whether the node is valid.
 */
Policy.prototype.isValid = function(node, root) {
  throw Error('Not implemented');
};


module.exports = Policy;
