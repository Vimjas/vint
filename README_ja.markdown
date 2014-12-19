![logo](https://raw.githubusercontent.com/Kuniwak/vint/logo/logo.png)

[![Development Status](https://pypip.in/status/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Latest Version](https://pypip.in/version/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Supported Python versions](https://pypip.in/py_versions/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Supported Python implementations](https://pypip.in/implementation/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Build Status](https://travis-ci.org/Kuniwak/vint.svg?branch=master)](https://travis-ci.org/Kuniwak/vint)

Vint は Vim script のための lint ツールです。
下のような lint を目指しています：

- 拡張性の高い lint
- 設定が柔軟にできる lint
- 高速に動作する lint

**Vint はまだ開発中なため安定していません。lint ルールの実装などにぜひ協力してください！**


インストール
------------

pip でインストールします。

	$ pip install vim-vint


設定
----

Vint は以下の優先順位で設定を読み込みます：

- [User config](#user-config):
  - e.g. `~/.vintrc.yaml`

- [Project config](#project-config):
  - e.g. `path/to/proj/.vintrc.yaml`

- [Command line config](#command-line-config):
  - e.g. `$ vint --error`, `$ vint --max-violations 10`

- [Comment config](#comment-config) (highest priority):
  - e.g. `" vint: -ProhibitAbbreviationOption +ProhibitSetNoCompatible`


### User config

`~/.vintrc.yaml` に、プロジェクトに依らない vint の設定を記述できます:

```yaml
cmdargs:
  # Checking more strictly
  severity: style

  # Enable coloring
  color: true

policies:
  # Disable a violation
  ProhibitSomethingEvil:
    enabled: false

  # Enable a violation
  ProhibitSomethingBad:
    enabled: true
```


### Project config

`.vintrc.yaml` に、プロジェクト固有の vint の設定を記述できます:

```yaml
cmdargs:
  # Checking more strictly
  severity: style

  # Enable coloring
  color: true

policies:
  # Disable a violation
  ProhibitSomethingEvil:
    enabled: false

  # Enable a violation
  ProhibitSomethingBad:
    enabled: true
```


### Command line config

コマンドライン引数から、彩色オプションや警告レベル等を制御できます:

	$ vint --color --style ~/.vimrc


### Comment config

lint ルールの有効化/無効化をコメントからおこなうことができます。


```viml
" vint: -ProhibitAbbreviationOption

let s:save_cpo = &cpo
set cpo&vim

" vint: +ProhibitAbbreviationOption

" do something...

" vint: -ProhibitAbbreviationOption

let &cpo = s:save_cpo
unlet s:save_cpo
```

この構文規則は次の通りです: `" vint: [+-]<PolicyName> [+-]<PolicyName> ...`


コードヘルス
------------

[![Coverage Status](https://img.shields.io/coveralls/Kuniwak/vint.svg)](https://coveralls.io/r/Kuniwak/vint)
[![Code Health](https://landscape.io/github/Kuniwak/vint/master/landscape.png)](https://landscape.io/github/Kuniwak/vint/master)


ライセンス
----------

[MIT](http://orgachem.mit-license.org/)


謝辞
----

* [ynkdir/vim-vimlparser](https://github.com/ynkdir/vim-vimlparser)
* [Google Vimscript Style Guide](http://google-styleguide.googlecode.com/svn/trunk/vimscriptguide.xml?showone=Catching_Exceptions#Catching_Exceptions)
