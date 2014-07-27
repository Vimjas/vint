path = require 'path'
chai = require 'chai'
expect = chai.expect

parser = require '../../../src/ast/parser.coffee'
linter = require '../../../src/lint.coffee'

describe 'Policy', () ->
  conditions = require '../../../test/src/policy/policy_test_conditions.json'
  conditions.map((condition) ->
    policyName = path.basename(condition.policy)
    it policyName, (done) ->
      policyPath = condition.policy
      pathToLint = condition.path
      expected_violations_count = condition.expected_violations

      Policy = require(path.join('..', '..', '..', policyPath))
      policy = new Policy()

      parser.parseFile(pathToLint, (err, ast) ->
        violations = linter.lint([policy], ast, { path: pathToLint })
        expect(violations).to.have.length(expected_violations_count)
        done()
      ))
