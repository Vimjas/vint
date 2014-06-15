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
 * Linting environment.
 * @typedef {{ path: string }}
 */
var Environment;


/**
 * A class for abstract validation policy.
 * @constructor
 */
function Policy() {
  this.violations = [];
  this.name = this.constructor.name;
  this.desc = null;
  this.ref = null;
  this.level = null;
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
 * @param {Environment} env Linting environment.
 */
Policy.prototype.handleNode = function(node, root, env) {
  var isValidNode = this.isValid(node, root);
  if (!isValidNode) {
    this.violations.push(this.createViolationReport(node.pos, env, node));
  }
};


/**
 * Creates a violation report.
 * @param {Position} pos Violation position.
 * @param {Environment} env Linting environment.
 * @return {Violation} Violation object.
 * @protected
 */
Policy.prototype.createViolationReport = function(pos, env) {
  return {
    name: this.name,
    level: this.level,
    desc: this.desc,
    ref: this.ref,
    path: env.path,
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
