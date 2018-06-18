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

This syntax is: ``" vint: [+-]<PolicyName> [+-]<PolicyName> ...``.

You can see all policy names on `Vint linting policy
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
