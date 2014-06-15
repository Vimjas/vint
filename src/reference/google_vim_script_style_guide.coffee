# @fileoverview Reference utility for Google VimScript Style Guide.
# @author orga.chem.job@gmail.com (Kuniwak)
# @see http://google-styleguide.googlecode.com/svn/trunk/vimscriptguide.xml

format = require('util').format


# Section names for Google VimScript Style Guide.
# @enum {string}
Sections =
  # Portability
  STRINGS:      'Strings'
  MATCHING:     'Matching'
  REGULAR:      'Regular'
  EXPRESSIONS:  'Expressions'
  DANGEROUS:    'Dangerous'
  COMMANDS:     'Commands'
  FRAGILE:      'Fragile'
  CATCHING:     'Catching'
  EXCEPTIONS:   'Exceptions'

  # General  Guidelines
  MESSAGING:    'Messaging'
  TYPE:         'Type'
  CHECKING:     'checking'
  PYTHON:       'Python'
  OTHER:        'Other'
  LANGUAGES:    'Languages'
  BOILERPLATE:  'Boilerplate'
  PLUGIN:       'Plugin'
  LAYOUT:       'Layout'
  FUNCTIONS:    'Functions'
  AUTOCOMMANDS: 'Autocommands'
  MAPPINGS:     'Mappings'
  SETTINGS:     'Settings'

  # Style
  WHITESPACE:   'Whitespace'
  NAMING:       'Naming'



# Returns a reference name for violations.
# This reference name should be search easy.
getReferenceSource = (section) ->
  format('Section %s at Google VimScript Style Guide', section)


module.exports =
  Sections: Sections
  getReferenceSource: getReferenceSource
