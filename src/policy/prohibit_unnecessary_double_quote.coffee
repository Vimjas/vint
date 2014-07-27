Policy = require('../policy')
NodeType = require('../ast/nodetype').NodeType
SeverityLevel = require('../level').SeverityLevel
Sections = require('../reference/google_vim_script_style_guide').Sections
getReferenceSource = require('../reference/google_vim_script_style_guide')
  .getReferenceSource


# A class for validation policy of double quoted string.
# @constructor
# @extends {Policy}
class ProhibitUnnecessaryDoubleQuote extends Policy
  constructor: () ->
    super()
    @desc = 'Prefer single quoted strings'
    @ref = getReferenceSource(Sections.STRINGS)
    @level = SeverityLevel.WARNING

  # @override
  listeningNodeType: () ->
    listeningNodeType = super()

    listeningNodeType.push(NodeType.STRING)
    return listeningNodeType


  # @override
  isValid: (node, root) ->
    isDoubleQuoted = node.value[0] == '"'

    return true if not isDoubleQuoted
    return STRING_SPECIAL_CHAR_MATCHER.test(node.value)


# Special character mathcer for string constants.
# @const
# @type {RegExp}
# @see `:help expr-string`
STRING_SPECIAL_CHAR_MATCHER = (() ->
  StringConstantSpecialChar =
    OCTAL:                       '[0-7]{1,3}',
    HEXADECIMAL:                 '[xX][0-9a-fA-F]{1,2}',
    NUMERIC_CHARACTER_REFERENCE: '[uU][0-9a-fA-F]{4}',
    BACKSPACE:                   'b',
    ESCAPE:                      'e',
    FORM_FEED:                   'f',
    NEW_LINE:                    'n',
    CARRIAGE_RETURN:             'r',
    TAB:                         't',
    BACKSLASH:                   '\\\\\\\\',
    DOUBLE_QUPTE:                '"',
    SPECIAL_KEY:                 '<[^>]+>',

  subRegExps = Object.keys(StringConstantSpecialChar).map((key) ->
    return StringConstantSpecialChar[key])

  return RegExp('\\\\(' + subRegExps.join('|') + ')'))()

module.exports = ProhibitUnnecessaryDoubleQuote
