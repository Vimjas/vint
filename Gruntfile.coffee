module.exports = (grunt) ->
  grunt.loadNpmTasks('grunt-contrib-coffee')
  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-jsonlint')
  grunt.loadNpmTasks('grunt-coffeelint')
  grunt.loadNpmTasks('grunt-mocha-test')

  grunt.initConfig(
    pkg: grunt.file.readJSON('package.json')

    coffee:
      glob_to_multiple:
        expand: true,
        flatten: true,
        cwd: 'src',
        src: ['**/*.coffee'],
        dest: 'lib',
        ext: '.js'

    coffeelint:
      files: ['src/**/*.coffee', 'test/**/*.coffee']
      options:
        globals:
          console: true
          module: true

    jsonlint:
      files: ['*.json', 'lib/**/*.json', 'test/**/*.json']

    mochaTest:
      test:
        src: ['test/**/*.coffee', '!test/fixture/**/*.coffee']
        options:
          reporter: 'spec'
          growl: true

    watch:
      files: ['<%= coffeelint.files %>', '<%= jsonlint.files %>']
      tasks: ['coffeelint', 'jsonlint', 'mochaTest', 'coffee']
  )

  grunt.registerTask('default', ['coffeelint', 'jsonlint', 'mochaTest'])
