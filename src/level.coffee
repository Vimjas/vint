# Lint level
# @enum {number}
SeverityLevel =
  REFACTOR:   4
  CONVENTION: 3
  WARNING:    2
  ERROR:      1
  FATAL:      0


# Returns an upper cased severity level name.
# @param {SeverityLevel} level Severity level.
# @return {string} Severity level name.
getSeverityLevelName = (() ->
  reverseMap = {}
  for levelName of SeverityLevel
    level = SeverityLevel[levelName]
    reverseMap[level] = levelName

  return (level) -> reverseMap[level])()

exports.SeverityLevel = SeverityLevel
exports.getSeverityLevelName = getSeverityLevelName
