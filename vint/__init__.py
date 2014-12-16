import sys
from argparse import ArgumentParser
import pkg_resources

from vint.linting.linter import Linter
from vint.linting.env import build_environment
from vint.linting.config.config_container import ConfigContainer
from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.config.config_default_source import ConfigDefaultSource
from vint.linting.config.config_global_source import ConfigGlobalSource
from vint.linting.config.config_project_source import ConfigProjectSource
from vint.linting.policy_set import PolicySet
from vint.linting.formatter.formatter import Formatter
from vint.linting.formatter.json_formatter import JSONFormatter
from vint.linting.formatter.statistic_formatter import StatisticFormatter


def main():
    env = _build_env(sys.argv)
    config_dict = _build_config_dict(env)
    parser = _build_argparser()

    paths_to_lint = env['file_paths']

    if len(paths_to_lint) == 0:
        print('vint error: nothing to lint\n')
        parser.print_help()
        parser.exit(status=1)

    for path_to_lint in paths_to_lint:
        if not path_to_lint.exists() or not path_to_lint.is_file():
            print('vint error: no such file: `{path}`\n'.format(
                path=str(path_to_lint)))
            parser.exit(status=1)

    violations = _lint_all(paths_to_lint, config_dict)

    if len(violations) == 0:
        parser.exit(status=0)

    _print_violations(violations, config_dict)
    parser.exit(status=1)


def _build_config_dict(env):
    config = ConfigContainer(
        ConfigDefaultSource(env),
        ConfigGlobalSource(env),
        ConfigProjectSource(env),
        ConfigCmdargsSource(env),
    )

    return config.get_config_dict()


def _build_argparser():
    parser = ArgumentParser(prog='vint', description='Lint Vim script')

    parser.add_argument('-v', '--version', action='version', version=_get_version())
    parser.add_argument('-V', '--verbose', action='store_true', help='output verbose message')
    parser.add_argument('-e', '--error', action='store_true', help='report only errors')
    parser.add_argument('-w', '--warning', action='store_true', help='report errors and warnings')
    parser.add_argument('-s', '--style-problem', action='store_true', help='report errors, warnings and style problems')
    parser.add_argument('-m', '--max-violations', type=int, help='limit max violations count')
    parser.add_argument('-c', '--color', action='store_true', help='colorize output when possible')
    parser.add_argument('-j', '--json', action='store_true', help='output json style')
    parser.add_argument('-t', '--stat', action='store_true', help='output statistic info')
    parser.add_argument('files', nargs='*', help='file or directory path to lint')

    return parser


def _build_cmdargs(argv):
    """ Build command line arguments dict to use;
    - displaying usages
    - vint.linting.env.build_environment

    This method take an argv parameter to make function pure.
    """
    parser = _build_argparser()
    namespace = parser.parse_args(argv[1:])

    cmdargs = vars(namespace)
    return cmdargs


def _build_env(argv):
    """ Build an environment object.
    This method take an argv parameter to make function pure.
    """
    cmdargs = _build_cmdargs(argv)
    env = build_environment(cmdargs)
    return env


def _build_linter(config_dict):
    policy_set = PolicySet()
    linter = Linter(policy_set, config_dict)
    return linter


def _lint_all(paths_to_lint, config_dict):
    violations = []
    linter = _build_linter(config_dict)

    for file_path in paths_to_lint:
        violations += linter.lint_file(file_path)

    return violations


def _get_formatter(config_dict):
    if 'cmdargs' not in config_dict:
        return Formatter(config_dict)

    cmdargs = config_dict['cmdargs']
    if 'json' in cmdargs and cmdargs['json']:
        return JSONFormatter(config_dict)
    elif 'stat' in cmdargs and cmdargs['stat']:
        return StatisticFormatter(config_dict)
    else:
        return Formatter(config_dict)


def _print_violations(violations, config_dict):
    formatter = _get_formatter(config_dict)
    output = formatter.format_violations(violations)

    print(output)


def _get_version():
    version = pkg_resources.require('vim-vint')[0].version
    return version
