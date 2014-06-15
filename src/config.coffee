fs = require('fs')
path = require('path')

policyPaths = fs.readdirSync('./lib/policy')

# Available policies.
# @type {Array.<Policies>}
Policies = []

policyPaths.forEach((policyPath) ->
  if path.extname(policyPath) != '.js'
    return

  Policy = require(path.join(__dirname, 'policy', policyPath))
  Policies.push(new Policy()))


# Returns an enabled policy.
# @param {SeverityLevel} level Severity level.
# @return {Array.<Policy>} Enabled policies.
getEnabledPolicies = (level) ->
  return Policies.filter((policy) -> return policy.level <= level)

module.exports =
  getEnabledPolicies: getEnabledPolicies
