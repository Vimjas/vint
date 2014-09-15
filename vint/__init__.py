from argparse import ArgumentParser
from vint.linting.linter import Linter
from vint.linting.formatter.formatter import Formatter
from vint.linting.env import build_environment
from vint.linting.config.config_container import ConfigContainer
from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.config.config_default_source import ConfigDefaultSource
from vint.linting.config.config_global_source import ConfigGlobalSource
from vint.linting.config.config_project_source import ConfigProjectSource
from vint.linting.policy_set import PolicySet

VERSION = '0.0.0'


def main(argv):
    env = _build_env(argv)
    config_dict = _build_config_dict(env)
    parser = _build_argparser()

    paths_to_lint = env['file_paths']

    if len(paths_to_lint) == 0:
        print('error: nothing to lint\n')
        parser.print_help()
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

    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('-V', '--verbose', action='store_true', help='output verbose message')
    parser.add_argument('-e', '--error', action='store_true', help='report only errors')
    parser.add_argument('-w', '--warning', action='store_true', help='report errors and warnings')
    parser.add_argument('-s', '--style-problem', action='store_true', help='report errors, warnings and style problems')
    parser.add_argument('-m', '--max-violations', type=int, help='limit max violations count')
    parser.add_argument('-c', '--color', action='store_true', help='colorize output when possible')
    parser.add_argument('-j', '--json', action='store_true', help='output json style')
    parser.add_argument('files', nargs='*', help='file or directory path to lint')

    return parser


def _build_cmdargs(argv):
    parser = _build_argparser()
    namespace = parser.parse_args(argv)

    cmdargs = vars(namespace)
    return cmdargs


def _build_env(argv):
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


def _print_violations(violations, env):
    formatter = Formatter(env)
    output = formatter.format_violations(violations)

    print(output)
