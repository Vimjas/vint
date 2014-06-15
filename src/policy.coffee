# Source code position.
# @typedef {{ i: number, lnum: number, col: number, path: string, ref: string }}
Position = null

# Violation object to report.
# @typedef {{ id: number, pos: Position, desc: string }}
Violation = null

# Linting environment.
# @typedef {{ path: string }}
Environment = null

# A class for abstract validation policy.
class Policy
  constructor: () ->
    @violations = []
    @name = @constructor.name
    @desc = null
    @ref = null
    @level = null

  # Returns a listening node type.
  # @return {Array.<NodeType>} Node type to listen.
  listeningNodeType: () -> []

  # Handles the specified node.
  # In default, store a violation object if the node has any violations.
  # @param {Node} node Vim language AST node to check.
  # @param {Node} root Root Vim language AST node.
  # @param {Environ} env Linting environment.
  handleNode: (node, root, env) ->
    if not @isValid(node, root)
      @violations.push(this.createViolationReport(node.pos, env, node))


  # Creates a violation report.
  # @param {Position} pos Violation position.
  # @param {Environment} env Linting environment.
  # @return {Violation} Violation object.
  # @protected
  createViolationReport: (pos, env) ->
    name: this.name
    level: this.level
    desc: this.desc
    ref: this.ref
    path: env.path
    pos: pos

  # Returns whether the specified node is valid to the policy.
  # @param {Node} node Vim language AST node to check.
  # @param {Node} root Root Vim language AST node.
  # @return {Boolean} Whether the node is valid.
  isValid: (node, root) -> throw Error('Not implemented')

module.exports = Policy
