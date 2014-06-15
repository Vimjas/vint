/**
 * @fileoverview Reference utility for Google VimScript Style Guide.
 * @author orga.chem.job@gmail.com (Kuniwak)
 * @see http://google-styleguide.googlecode.com/svn/trunk/vimscriptguide.xml
 */


var format = require('util').format;


/**
 * Section names for Google VimScript Style Guide.
 * @enum {string}
 */
var Sections = {
  // Portability
  STRINGS: 'Strings',
  MATCHING: 'Matching',
  STRINGS: 'Strings',
  REGULAR: 'Regular',
  EXPRESSIONS: 'Expressions',
  DANGEROUS: 'Dangerous',
  COMMANDS: 'commands',
  FRAGILE: 'Fragile',
  COMMANDS: 'commands',
  CATCHING: 'Catching',
  EXCEPTIONS: 'Exceptions',

  // General Guidelines
  MESSAGING: 'Messaging',
  TYPE: 'Type',
  CHECKING: 'checking',
  PYTHON: 'Python',
  OTHER: 'Other',
  LANGUAGES: 'Languages',
  BOILERPLATE: 'Boilerplate',
  PLUGIN: 'Plugin',
  LAYOUT: 'layout',
  FUNCTIONS: 'Functions',
  COMMANDS: 'Commands',
  AUTOCOMMANDS: 'Autocommands',
  MAPPINGS: 'Mappings',
  SETTINGS: 'Settings',

  // Style
  WHITESPACE: 'Whitespace',
  NAMING: 'Naming',
};


/**
 * Returns a reference name for violations.
 * This reference name should be search easy.
 */
var getReferenceSource = function(section) {
  return format('Section %s at Google VimScript Style Guide', section);
};


exports.Sections = Sections;
exports.getReferenceSource = getReferenceSource;
