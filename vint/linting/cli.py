import sys
from argparse import ArgumentParser
from pathlib import PosixPath
import pkg_resources
import logging

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

class CLI(object):
    def start(self):
        env = self._build_env(sys.argv)
        self._validate(env)

        self._adjust_log_level(env)

        config_dict = self._build_config_dict(env)
        violations = self._lint_all(env, config_dict)

        parser = self._build_argparser()

        if len(violations) == 0:
            parser.exit(status=0)

        self._print_violations(violations, config_dict)
        parser.exit(status=1)


    def _validate(self, env):
        parser = self._build_argparser()
        paths_to_lint = env['file_paths']

        if len(paths_to_lint) == 0:
            logging.error('nothing to check')
            parser.print_help()
            parser.exit(status=1)

        if not self._should_read_from_stdin(env):
            for path_to_lint in paths_to_lint:
                if not path_to_lint.exists() or not path_to_lint.is_file():
                    logging.error('no such file or directory: `{path}`'.format(
                        path=str(path_to_lint)))
                    parser.exit(status=1)


    def _build_config_dict(self, env):
        config = ConfigContainer(
            ConfigDefaultSource(env),
            ConfigGlobalSource(env),
            ConfigProjectSource(env),
            ConfigCmdargsSource(env),
        )

        return config.get_config_dict()


    def _build_argparser(self):
        parser = ArgumentParser(prog='vint', description='Lint Vim script')

        parser.add_argument('-v', '--version', action='version', version=self._get_version())
        parser.add_argument('-V', '--verbose', action='store_const', const=True, help='output verbose message')
        parser.add_argument('-e', '--error', action='store_const', const=True, help='report only errors')
        parser.add_argument('-w', '--warning', action='store_const', const=True, help='report errors and warnings')
        parser.add_argument('-s', '--style-problem', action='store_const', const=True, help='report errors, warnings and style problems')
        parser.add_argument('-m', '--max-violations', type=int, help='limit max violations count')
        parser.add_argument('-c', '--color', action='store_const', const=True, help='colorize output when possible')
        parser.add_argument('--no-color', action='store_const', const=True, help='do not colorize output')
        parser.add_argument('-j', '--json', action='store_const', const=True, help='output json style')
        parser.add_argument('-t', '--stat', action='store_const', const=True, help='output statistic info')
        parser.add_argument('--enable-neovim', action='store_const', const=True, help='Enable Neovim syntax')
        parser.add_argument('-f', '--format', help='set output format')
        parser.add_argument('files', nargs='*', help='file or directory path to lint')

        return parser


    def _build_cmdargs(self, argv):
        """ Build command line arguments dict to use;
        - displaying usages
        - vint.linting.env.build_environment

        This method take an argv parameter to make function pure.
        """
        parser = self._build_argparser()
        namespace = parser.parse_args(argv[1:])

        cmdargs = vars(namespace)
        return cmdargs


    def _build_env(self, argv):
        """ Build an environment object.
        This method take an argv parameter to make function pure.
        """
        cmdargs = self._build_cmdargs(argv)
        env = build_environment(cmdargs)
        return env


    def _build_linter(self, config_dict):
        policy_set = PolicySet()
        linter = Linter(policy_set, config_dict)
        return linter


    def _lint_all(self, env, config_dict):
        paths_to_lint = env['file_paths']
        violations = []
        linter = self._build_linter(config_dict)

        if self._should_read_from_stdin(env):
            violations += linter.lint_text(sys.stdin.read())
        else:
            for file_path in paths_to_lint:
                violations += linter.lint_file(file_path)

        return violations

    def _should_read_from_stdin(self, env):
        return len(env['file_paths']) == 1 and PosixPath('-') in env['file_paths']


    def _get_formatter(self, config_dict):
        if 'cmdargs' not in config_dict:
            return Formatter(config_dict)

        cmdargs = config_dict['cmdargs']
        if 'json' in cmdargs and cmdargs['json']:
            return JSONFormatter(config_dict)
        elif 'stat' in cmdargs and cmdargs['stat']:
            return StatisticFormatter(config_dict)
        else:
            return Formatter(config_dict)


    def _print_violations(self, violations, config_dict):
        formatter = self._get_formatter(config_dict)
        output = formatter.format_violations(violations)

        print(output)


    def _get_version(self):
        # In unit tests, pkg_resources cannot find vim-vint.
        # So, I decided to return dummy version
        try:
            version = pkg_resources.require('vim-vint')[0].version
        except pkg_resources.DistributionNotFound:
            version = 'test_mode'

        return version


    def _adjust_log_level(self, env):
        cmdargs = env['cmdargs']

        is_verbose = cmdargs.get('verbose', False)
        log_level = logging.DEBUG if is_verbose else logging.WARNING

        logger = logging.getLogger()
        logger.setLevel(log_level)
