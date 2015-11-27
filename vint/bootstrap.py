import importlib
import pkgutil
from pathlib import Path

from vint.linting.cli import CLI
import logging


LOG_FORMAT = 'vint %(levelname)s: %(message)s'


def init_logger():
    logging.basicConfig(format=LOG_FORMAT)


def init_linter():
    import_all_policies()


def init_cli():
    cli = CLI()
    cli.start()


def import_all_policies():
    """ Import all policies that were registered by vint.linting.policy_registry.

    Dynamic policy importing is comprised of the 3 steps
      1. Try to import all policy modules (then we can't know what policies exist)
      2. In policy module, register itself by using vint.linting.policy_registry
      3. After all policies registered by itself, we can get policy classes
    """
    pkg_name = _get_policy_package_name_for_test()
    pkg_path_list = pkg_name.split('.')

    pkg_path = str(Path(_get_vint_root(), *pkg_path_list).resolve())

    for _, module_name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if not is_pkg:
            module_fqn = pkg_name + '.' + module_name
            logging.debug('Loading the policy module: `{fqn}`'.format(fqn=module_fqn))
            importlib.import_module(module_fqn)


def _get_vint_root():
    return Path(__file__).parent.parent


def _get_policy_package_name_for_test():
    """ Test hook method that returns a package name for policy modules. """
    return 'vint.linting.policy'
