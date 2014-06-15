var fs = require('fs');
var path = require('path');

var policyPaths = fs.readdirSync('./policy');

/**
 * Available policies.
 * @type {Array.<Policies>}
 */
var Policies = [];

policyPaths.forEach(function(policyPath) {
  if (path.extname(policyPath) !== '.js') return;

  var Policy = require(path.join('policy', policyPath));
  Policies.push(new Policy());
});


/**
 * Returns an enabled policy.
 * @param {SeverityLevel} level Severity level.
 * @return {Array.<Policy>} Enabled policies.
 */
function getEnabledPolicies(level) {
  return Policies.filter(function(policy) {
    return policy.level <= level;
  });
}

module.exports = {
  getEnabledPolicies: getEnabledPolicies,
};
