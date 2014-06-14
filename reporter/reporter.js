/**
 * A class for violation reporters.
 * @constructor
 */
function Reporter() {
  /**
   * Format pattern to report violation.
   * <pre>
   * Escape    Meaning
   * -------   ----------------------------------------------------------------
   * %c        Column number where the violation occurred
   * %r        Reference for the violation occurred
   * %f        Path to the logical file where the violation occurred.
   * %l        Logical line number where the violation occurred
   * %m        Brief description of the violation
   * %p        Name of the Policy
   * %s        The severity level of the violation
   * </pre>
   * @type {string}
   */
  this.formatPattern = '%m at line %l, column %c. %r.';
}


/**
 * Returns a formated violation report.
 * @param {Violation} violation Violation to report.
 * @return {string} Violation report.
 */
Reporter.prototype.format = function(violation) {
  var formated = this.formatPattern.replace(/%([crflmps])/g, function(match, char) {
    switch (char) {
      case 'c': return violation.pos.col;
      case 'r': return violation.ref;
      case 'f': return violation.path;
      case 'l': return violation.pos.lnum;
      case 'm': return violation.desc;
      case 'p': return violation.name;
      case 's': return violation.level;
    }
  });

  return formated;
};


/**
 * Returns an violations report.
 * @param {Array.<Violation>} violation Violations to report.
 * @return {string} Violations report.
 */
Reporter.prototype.formatAll = function(violations) {
  var that = this;
  return violations.map(function(violation) {
    return that.format(violation);
  }).join('\n');
}

module.exports = Reporter;
