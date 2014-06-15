
# A class for violation reporters.
# @constructor
class Reporter
  constructor: () ->
    # Format pattern to report violation.
    # <pre>
    # Escape    Meaning
    # -------   ----------------------------------------------------------------
    # %c        Column number where the violation occurred
    # %r        Reference for the violation occurred
    # %f        Path to the logical file where the violation occurred.
    # %l        Logical line number where the violation occurred
    # %m        Brief description of the violation
    # %p        Name of the Policy
    # %s        The severity level of the violation
    # </pre>
    # @type {string}
    @formatPattern = '%m at line %l, column %c. %r.'


  # Returns a formated violation report.
  # @param {Violation} violation Violation to report.
  # @return {string} Violation report.
  format: (violation) ->
    formated = @formatPattern.replace(/%([crflmps])/g, (match, char) ->
      switch char
        when 'c' then return violation.pos.col
        when 'r' then return violation.ref
        when 'f' then return violation.path
        when 'l' then return violation.pos.lnum
        when 'm' then return violation.desc
        when 'p' then return violation.name
        when 's' then return violation.level)

    return formated



  # Returns an violations report.
  # @param {Array.<Violation>} violation Violations to report.
  # @return {string} Violations report.
  formatAll: (violations) ->
    violations.map((violation) =>
      return @format(violation)).join('\n')

module.exports = Reporter
