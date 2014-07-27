fs = require('fs')

VimLParser = require('../../extlib/vimlparser.js')


# Parses a file of the specified path to AST.
# @param {string} file File path.
# @param {function(Error, Object)} callback Callback function.
#   The first argument is error if exists. The second argument is AST.
parseFile = (file, callback) ->
  fs.readFile(file, 'utf-8', (err, content) ->
    throw err if err

    ast = parseString(content)
    callback(err, ast))


# Parses the specified string to AST.
# @param {string}
# @return {Object} AST.
parseString = (str) ->
  lines = str.split(/\r\n|\r|\n/)
  parser = new VimLParser.VimLParser()
  stringReader = new VimLParser.StringReader(lines)
  ast = parser.parse(stringReader)
  return ast


module.exports =
  parseFile: parseFile,
  parseString: parseString,
