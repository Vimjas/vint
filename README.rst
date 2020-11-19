.. figure:: https://raw.githubusercontent.com/Kuniwak/vint/logo/logo.png
   :alt: logo

----

|Development Status| |Latest Version| |Supported Python versions|
|Supported Python implementations| |Build Status|

Vint is a Vim script Language Lint. The goal to reach for Vint is:

-  Highly extensible
-  Highly customizable
-  High performance

**But now, Vint is under development. We hope you develop a policy to
help us.**

Quick start
-----------

You can install with `pip <https://pip.pypa.io/en/latest/>`__.

::

    $ pip install vim-vint

You can use Vint with
`vim-syntastic/syntastic <https://github.com/vim-syntastic/syntastic>`__::

    let g:syntastic_vim_checkers = ['vint']
    
Or with `coc.nvim <https://github.com/neoclide/coc.nvim>`__ and
`iamcco/diagnostic-languageserver <https://github.com/iamcco/diagnostic-languageserver>`__::
    {
      "languageserver": {
        "dls": {
          "command": "diagnostic-languageserver",
          "args": ["--stdio"],
          "filetypes": ["vim"],
          "initializationOptions": {
            "linters": {
              "vint": {
                "command": "vint",
                "debounce": 100,
                "args": ["--enable-neovim", "-"],
                "offsetLine": 0,
                "offsetColumn": 0,
                "sourceName": "vint",
                "formatLines": 1,
                "formatPattern": [
                  "[^:]+:(\\d+):(\\d+):\\s*(.*)(\\r|\\n)*$",
                  {
                    "line": 1,
                    "column": 2,
                    "message": 3
                  }
                ]
              }
            },
            "filetypes": {
              "vim": "vint"
            }
          }
        }
      }
    }


Configure
---------

Vint will read config files on the following priority order:

-  `User config <#user-config>`__:
-  e.g. ``~/.vintrc.yaml`` (the filename can be ``.vintrc.yml`` or ``.vintrc``)

-  `Project config <#project-config>`__:
-  e.g. ``path/to/proj/.vintrc.yaml`` (the filename can be ``.vintrc.yml`` or ``.vintrc``)

-  `Command line config <#command-line-config>`__:
-  e.g. ``$ vint --error``, ``$ vint --max-violations 10``

-  `Comment config <#comment-config>`__ (highest priority):
-  e.g. ``" vint: -ProhibitAbbreviationOption +ProhibitSetNoCompatible``

You can see all options on `Wiki <https://github.com/Kuniwak/vint/wiki/Config>`__.

The default configuration is defined in
`default_config.yaml <vint/asset/default_config.yaml>`_.


User config
~~~~~~~~~~~

You can configure global Vint config by ``~/.vintrc.yaml`` as following:

.. code:: yaml

    cmdargs:
      # Checking more strictly
      severity: style_problem

      # Enable coloring
      color: true

      # Enable Neovim syntax
      env:
        neovim: true

    policies:
      # Disable a violation
      ProhibitSomethingEvil:
        enabled: false

      # Enable a violation
      ProhibitSomethingBad:
        enabled: true

You can see all policy names on `Vint linting policy
summary <https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary>`__.

Project config
~~~~~~~~~~~~~~

You can configure project local Vint config by ``.vintrc.yaml`` as
following:

.. code:: yaml

    cmdargs:
      # Checking more strictly
      severity: style_problem

      # Enable coloring
      color: true

      # Enable Neovim syntax
      env:
        neovim: true

    policies:
      # Disable a violation
      ProhibitSomethingEvil:
        enabled: false

      # Enable a violation
      ProhibitSomethingBad:
        enabled: true

You can see all policy names on `Vint linting policy
summary <https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary>`__.

Command line config
~~~~~~~~~~~~~~~~~~~

You can configure linting severity, max errors, ... as following:

::

    $ vint --color --style ~/.vimrc

And you can see all available options by using `--help`:

::

    $ vint --help
    usage: vint [-h] [-v] [-V] [-e] [-w] [-s] [-m MAX_VIOLATIONS] [-c]
                [--no-color] [-j] [-t] [--enable-neovim] [-f FORMAT]
                [--stdin-display-name STDIN_DISPLAY_NAME]
                [files [files ...]]

    Lint Vim script

    positional arguments:
      files                 file or directory path to lint

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -V, --verbose         output verbose message
      -e, --error           report only errors
      -w, --warning         report errors and warnings
      -s, --style-problem   report errors, warnings and style problems
      -m MAX_VIOLATIONS, --max-violations MAX_VIOLATIONS
                            limit max violations count
      -c, --color           colorize output when possible
      --no-color            do not colorize output
      -j, --json            output json style
      -t, --stat            output statistic info
      --enable-neovim       enable Neovim syntax
      -f FORMAT, --format FORMAT
                            set output format
      --stdin-display-name STDIN_DISPLAY_NAME
                            specify a file path that is used for reporting when
                            linting standard inputs

Comment config
~~~~~~~~~~~~~~

You can enable/disable linting policies by a comment as following:

.. code:: vim

    " vint: -ProhibitAbbreviationOption

    let s:save_cpo = &cpo
    set cpo&vim

    " vint: +ProhibitAbbreviationOption

    " do something...

    " vint: -ProhibitAbbreviationOption

    let &cpo = s:save_cpo
    unlet s:save_cpo

And you can use line config comments. It can enable/disable linting policies in only one line by the postfix comment:

.. code:: vim

    " vint: next-line -ProhibitUnusedVariable
    let s:foobar = 'x'
    echo s:{'foo' . 'bar'}

This syntax is: `" vint: [next-line] [+-]<PolicyName> [+-]<PolicyName> ...`.
You can see all policy names on `Vint linting policy summary <https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary>`__.

Code health
-----------

|Coverage Status| |Code Health| |Dependency Status|

License
-------

`MIT <http://orgachem.mit-license.org/>`__

Acknowledgement
---------------

-  `vim-jp/vim-vimlparser <https://github.com/vim-jp/vim-vimlparser>`__
-  `Google Vimscript Style
   Guide <https://google.github.io/styleguide/vimscriptguide.xml>`__
-  `Anti-pattern of
   vimrc <http://rbtnn.hateblo.jp/entry/2014/12/28/010913>`__

.. |Development Status| image:: https://img.shields.io/pypi/status/vim-vint.svg
   :target: https://pypi.python.org/pypi/vim-vint/
.. |Latest Version| image:: https://img.shields.io/pypi/v/vim-vint.svg
   :target: https://pypi.python.org/pypi/vim-vint/
.. |Supported Python versions| image:: https://img.shields.io/pypi/pyversions/vim-vint.svg
   :target: https://pypi.python.org/pypi/vim-vint/
.. |Supported Python implementations| image:: https://img.shields.io/pypi/implementation/vim-vint.svg
   :target: https://pypi.python.org/pypi/vim-vint/
.. |Build Status| image:: https://travis-ci.org/Vimjas/vint.svg?branch=master
   :target: https://travis-ci.org/Vimjas/vint
.. |Coverage Status| image:: https://img.shields.io/coveralls/Kuniwak/vint.svg
   :target: https://coveralls.io/r/Kuniwak/vint
.. |Code Health| image:: https://landscape.io/github/Kuniwak/vint/master/landscape.png
   :target: https://landscape.io/github/Kuniwak/vint/master
.. |Dependency Status| image:: https://gemnasium.com/Kuniwak/vint.svg
   :target: https://gemnasium.com/Kuniwak/vint
