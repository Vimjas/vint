from typing import Dict, Any, List  # noqa: F401
import sys
from argparse import ArgumentParser
from pathlib import Path
import logging

from vint.linting.linter import Linter
from vint.linting.env import build_environment
from vint.linting.config.config_container import ConfigContainer, ConfigEmptyEntryException
from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.config.config_default_source import ConfigDefaultSource
from vint.linting.config.config_global_source import ConfigGlobalSource
from vint.linting.config.config_project_source import ConfigProjectSource
from vint.linting.config.config_util import get_config_value
from vint.linting.lint_target import (
    AbstractLintTarget,
    LintTargetFile,
    LintTargetBufferedStream,
    CachedLintTarget,
)
from vint.linting.policy_set import PolicySet
from vint.linting.formatter.abstract_formatter import AbstractFormatter
from vint.linting.policy_registry import get_policy_classes
from vint.linting.formatter.formatter import Formatter
from vint.linting.formatter.json_formatter import JSONFormatter
from vint.linting.formatter.statistic_formatter import StatisticFormatter

_stdin_symbol = Path('-')


def start_cli():
    env = _build_env(sys.argv)
    _validate(env)

    _adjust_log_level(env)

    try:
        config_dict = _build_config_dict(env)
    except ConfigEmptyEntryException as e:
        sys.stderr.write("[error] " + str(e) + "\n")
        sys.exit(1)
    violations = _lint_all(env, config_dict)

    parser = _build_arg_parser()

    if len(violations) == 0:
        parser.exit(status=0)

    _print_violations(violations, config_dict)
    parser.exit(status=1)


def _validate(env):  # type: (Dict[str, Any]) -> None
    parser = _build_arg_parser()
    paths_to_lint = env['file_paths']

    if len(paths_to_lint) == 0:
        logging.error('nothing to check')
        parser.print_help()
        parser.exit(status=1)

    if paths_to_lint.count(_stdin_symbol) > 1:
        logging.error('number of "-" must be less than 2')
        parser.exit(status=1)

    for path_to_lint in filter(lambda path: path != _stdin_symbol, paths_to_lint):
        if not path_to_lint.exists() or not path_to_lint.is_file():
            logging.error('no such file or directory: `{path}`'.format(
                path=str(path_to_lint)))
            parser.exit(status=1)


def _build_env(argv):
    """ Build an environment object.
    This method take an argv parameter to make function pure.
    """
    cmdargs = _build_cmdargs(argv)
    env = build_environment(cmdargs)
    return env


def _build_cmdargs(argv):
    """ Build command line arguments dict to use;
    - displaying usages
    - vint.linting.env.build_environment

    This method take an argv parameter to make function pure.
    """
    parser = _build_arg_parser()
    namespace = parser.parse_args(argv[1:])

    cmdargs = vars(namespace)
    return cmdargs


def _build_arg_parser():
    parser = ArgumentParser(prog='vint', description='Lint Vim script')

    parser.add_argument('-v', '--version', action='version', version=_get_version())
    parser.add_argument('-V', '--verbose', action='store_const', const=True, help='output verbose message')
    parser.add_argument('-e', '--error', action='store_const', const=True, help='report only errors')
    parser.add_argument('-w', '--warning', action='store_const', const=True, help='report errors and warnings')
    parser.add_argument('-s', '--style-problem', action='store_const', const=True, help='report errors, warnings and style problems')
    parser.add_argument('-m', '--max-violations', type=int, help='limit max violations count')
    parser.add_argument('-c', '--color', action='store_const', const=True, help='colorize output when possible')
    parser.add_argument('--no-color', action='store_const', const=True, help='do not colorize output')
    parser.add_argument('-j', '--json', action='store_const', const=True, help='output json style')
    parser.add_argument('-t', '--stat', action='store_const', const=True, help='output statistic info')
    parser.add_argument('--enable-neovim', action='store_const', const=True, help='enable Neovim syntax')
    parser.add_argument('-f', '--format', help='set output format')
    parser.add_argument('--stdin-display-name', type=str, help='specify a file path that is used for reporting when linting standard inputs')
    parser.add_argument('files', nargs='*', help='file or directory path to lint')

    return parser


def _build_config_dict(env):  # type: (Dict[str, Any]) -> Dict[str, Any]
    config = ConfigContainer(
        ConfigDefaultSource(env),
        ConfigGlobalSource(env),
        ConfigProjectSource(env),
        ConfigCmdargsSource(env),
    )

    return config.get_config_dict()


def _lint_all(env, config_dict):  # type: (Dict[str, Any], Dict[str, Any]) -> List[Dict[str, Any]]
    paths_to_lint = env['file_paths']
    violations = []
    linter = _build_linter(config_dict)

    for path in paths_to_lint:
        lint_target = _build_lint_target(path, config_dict)
        violations += linter.lint(lint_target)

    return violations


def _build_linter(config_dict):  # type: (Dict[str, Any]) -> Linter
    policy_set = PolicySet(get_policy_classes())
    linter = Linter(policy_set, config_dict)
    return linter


def _print_violations(violations, config_dict):  # type: (List[Dict[str, Any]], Dict[str, Any]) -> None
    formatter = _build_formatter(config_dict)
    output = formatter.format_violations(violations)

    print(output)


def _build_formatter(config_dict):  # type: (Dict[str, Any]) -> AbstractFormatter
    if 'cmdargs' not in config_dict:
        return Formatter(config_dict)

    cmdargs = config_dict['cmdargs']
    if 'json' in cmdargs and cmdargs['json']:
        return JSONFormatter()
    elif 'stat' in cmdargs and cmdargs['stat']:
        return StatisticFormatter(config_dict)
    else:
        return Formatter(config_dict)


def _get_version():
    from ..__version__ import version
    return version


def _adjust_log_level(env):
    cmdargs = env['cmdargs']

    is_verbose = cmdargs.get('verbose', False)
    log_level = logging.DEBUG if is_verbose else logging.WARNING

    logger = logging.getLogger()
    logger.setLevel(log_level)


def _build_lint_target(path, config_dict):  # type: (Path, Dict[str, Any]) -> AbstractLintTarget
    if path == _stdin_symbol:
        stdin_alt_path = get_config_value(config_dict, ['cmdargs', 'stdin_display_name'])

        # NOTE: In Python 3, sys.stdin is a string not bytes. Then we can get bytes by sys.stdin.buffer.
        #       But in Python 2, sys.stdin.buffer is not defined. But we can get bytes by sys.stdin directly.
        is_python_3 = hasattr(sys.stdin, 'buffer')
        if is_python_3:
            lint_target = LintTargetBufferedStream(
                alternate_path=Path(stdin_alt_path),
                buffered_io=sys.stdin.buffer
            )
        else:
            # NOTE: Python 2 on Windows opens sys.stdin in text mode, and
            # binary data that read from it becomes corrupted on \r\n
            # SEE: https://stackoverflow.com/questions/2850893/reading-binary-data-from-stdin/38939320#38939320
            if sys.platform == 'win32':
                # set sys.stdin to binary mode
                import os, msvcrt
                msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)

            lint_target = LintTargetBufferedStream(
                alternate_path=Path(stdin_alt_path),
                buffered_io=sys.stdin
            )

        return CachedLintTarget(lint_target)

    else:
        lint_target = LintTargetFile(path)
        return CachedLintTarget(lint_target)
