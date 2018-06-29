![Vint](https://raw.githubusercontent.com/Kuniwak/vint/logo/logo.png)

----

[![](https://img.shields.io/pypi/status/vim-vint.svg)](https://pypi.python.org/pypi/vim-vint/)
[![](https://img.shields.io/pypi/v/vim-vint.svg)](https://pypi.python.org/pypi/vim-vint/)
[![](https://pypi.python.org/pypi/vim-vint/)](https://img.shields.io/pypi/pyversions/vim-vint.svg)
[![](https://img.shields.io/pypi/implementation/vim-vint.svg)](https://pypi.python.org/pypi/vim-vint/)
[![](https://travis-ci.org/Kuniwak/vint.svg?branch=master)](https://travis-ci.org/Kuniwak/vint)

Vint is a Vim script Language Lint. The goal to reach for Vint is:

-  Highly extensible
-  Highly customizable
-  High performance

**But now, Vint is under development. We hope you develop a policy to
help us.**



Quick start
-----------

You can install with [pip](https://pip.pypa.io/en/latest/).

```console
$ pip install vim-vint
```

You can use Vint with [scrooloose/syntastic](https://github.com/scrooloose/syntastic)

```vim
let g:syntastic_vim_checkers = ['vint']
```



Configure
---------

Vint will read config files on the following priority order:

-  [User config](#user-config):
-  e.g. `~/.vintrc.yaml` (the filename can be `.vintrc.yml` or `.vintrc`)

-  [Project config](#project-config):
-  e.g. `path/to/proj/.vintrc.yaml` (the filename can be `.vintrc.yml` or `.vintrc`)

-  [command line config](#command-line-config):
-  e.g. `$ vint --error`, `$ vint --max-violations 10`

-  [Comment config](#comment-config) (highest priority):
-  e.g. `" vint: -ProhibitAbbreviationOption +ProhibitSetNoCompatible`

You can see all options on [Wiki](https://github.com/Kuniwak/vint/wiki/Config).

The default configuration is defined in [`default_config.yaml`](vint/asset/default_config.yaml).



### User config

You can configure global Vint config by `~/.vintrc.yaml` as following:

```yaml
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
```

You can see all policy names on [Vint linting policy summary](https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary).



### Project config

You can configure project local Vint config by `.vintrc.yaml` as
following:

```yaml
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
```

You can see all policy names on [Vint linting policy summary](https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary).



### Command line config

You can configure linting severity, max errors, ... as following:

```console
$ vint --color --style ~/.vimrc
```

And you can see all available options by using `--help`:

```console
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
```


### Comment config

You can enable/disable linting policies by a comment as following:

```vim
" vint: -ProhibitAbbreviationOption

let s:save_cpo = &cpo
set cpo&vim

" vint: +ProhibitAbbreviationOption

" do something...

" vint: -ProhibitAbbreviationOption

let &cpo = s:save_cpo
unlet s:save_cpo
```

And you can use line config comments. It can enable/disable linting policies in only one line by the postfix comment:

```vim
" vint: next-line -ProhibitUnusedVariable
let s:foobar = 'x'
echo s:{'foo' . 'bar'}
```

This syntax is: `" vint: [next-line] [+-]<PolicyName> [+-]<PolicyName> ...`.
You can see all policy names on [Vint linting policy summary](https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary).



Code Health
-----------

[![](https://img.shields.io/coveralls/Kuniwak/vint.svg)](https://coveralls.io/r/Kuniwak/vint)
[![](https://landscape.io/github/Kuniwak/vint/master)](https://landscape.io/github/Kuniwak/vint/master/landscape.png)



License
-------

[MIT](http://orgachem.mit-license.org/)



Acknowledgement
---------------

- [vim-jp/vim-vimlparser](https://github.com/vim-jp/vim-vimlparser)
- [Google Vimscript Style Guide](https://google.github.io/styleguide/vimscriptguide.xml)
- [Anti-pattern of vimrc](http://rbtnn.hateblo.jp/entry/2014/12/28/010913)
