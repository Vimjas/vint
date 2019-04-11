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
`scrooloose/syntastic <https://github.com/scrooloose/syntastic>`__::

    let g:syntastic_vim_checkers = ['vint']

Configure
---------

Vint will read config files from files named ``.vintrc.yaml``, ``.vintrc.yml``,
or ``.vintrc``.

1. any of these files is read from your home directory.

2. any of these files is read based on the current directory, which allows for
   project specific settings.

3. `Command line options <#command-line-options>`__, e.g. ``--error``, or
   ``--max-violations``.

4.  `Comment directives <#comment-directives>`__ (highest priority), e.g.
    ``" vint: -ProhibitAbbreviationOption +ProhibitSetNoCompatible``.

The config options are documented in the `Wiki <https://github.com/Kuniwak/vint/wiki/Config>`__.

The default configuration is defined in
`default_config.yaml <vint/asset/default_config.yaml>`_.

Example configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

The policy names are documented in `Vint linting policy
summary <https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary>`__.

Command line options
~~~~~~~~~~~~~~~~~~~~

The following command line options are available:

::

    $ vint --help
    usage: vint [-h] [-v] [-V] [-e] [-w] [-s] [-m MAX_VIOLATIONS] [-c]
                [--no-color] [-j] [-t] [--enable-neovim] [-f FORMAT]
                [--stdin-alt-path STDIN_ALT_PATH]
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

Comment directives
~~~~~~~~~~~~~~~~~~

You can enable/disable linting policies through code comments as follows:

.. code:: vim

    " vint: -ProhibitAbbreviationOption

    let s:save_cpo = &cpo
    set cpo&vim

    " vint: +ProhibitAbbreviationOption

    " do something...

    " vint: -ProhibitAbbreviationOption

    let &cpo = s:save_cpo
    unlet s:save_cpo

You can also configure policies only for the following line:

.. code:: vim

    " vint: next-line -ProhibitUnusedVariable
    let s:foobar = 'x'
    echo s:{'foo' . 'bar'}

The syntax is: `" vint: [next-line] [+-]<PolicyName> [+-]<PolicyName> ...`.

The policy names are documented in `Vint linting policy
summary <https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary>`__.

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
.. |Build Status| image:: https://travis-ci.org/Kuniwak/vint.svg?branch=master
   :target: https://travis-ci.org/Kuniwak/vint
.. |Coverage Status| image:: https://img.shields.io/coveralls/Kuniwak/vint.svg
   :target: https://coveralls.io/r/Kuniwak/vint
.. |Code Health| image:: https://landscape.io/github/Kuniwak/vint/master/landscape.png
   :target: https://landscape.io/github/Kuniwak/vint/master
.. |Dependency Status| image:: https://gemnasium.com/Kuniwak/vint.svg
   :target: https://gemnasium.com/Kuniwak/vint
