/**
 * Lint level
 * @enum {number}
 */
var SeverityLevel = {
  REFACTOR: 4,
  CONVENTION: 3,
  WARNING: 2,
  ERROR: 1,
  FATAL: 0,
};


/**
 * Returns an upper cased severity level name.
 * @param {SeverityLevel} level Severity level.
 * @return {string} Severity level name.
 */
var getSeverityLevelName = (function() {
  var reverseMap = {};
  Object.keys(SeverityLevel).forEach(function(levelName) {
    var level = SeverityLevel[levelName];
    reverseMap[level] = levelName;
  });

  return function getSeverityLevelName(level) {
    return reverseMap[level];
  };
})();


exports.SeverityLevel = SeverityLevel;
exports.getSeverityLevelName = getSeverityLevelName;
