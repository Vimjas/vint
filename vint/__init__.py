import sys
from vint.linting.linter import Linter
from vint.linting.formatter.formatter import Formatter
from vint.linting.env import build_environment
from vint.linting.config.config_container import ConfigContainer
from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.config.config_default_source import ConfigDefaultSource
from vint.linting.config.config_global_source import ConfigGlobalSource
from vint.linting.config.config_project_source import ConfigProjectSource
from vint.linting.policy_set import PolicySet


def build_config_dict(env):
    config = ConfigContainer(
        ConfigDefaultSource(env),
        ConfigGlobalSource(env),
        ConfigProjectSource(env),
        ConfigCmdargsSource(env),
    )

    return config.get_config_dict()


def main(argv):
    env = build_environment(argv)
    paths_to_lint = env['file_paths']

    policy_set = PolicySet()
    config_dict = build_config_dict(env)

    linter = Linter(policy_set, config_dict)
    violations = []

    for file_path in paths_to_lint:
        violations += linter.lint_file(file_path)

    if len(violations) == 0:
        sys.exit(0)

    formatter = Formatter(env)
    output = formatter.format_violations(violations)

    print(output)

    sys.exit(1)
