import importlib
import logging
import pkgutil
from pathlib import Path
from vint.linting.policy_loader import get_policy_class_map


class PolicySet(object):
    def __init__(self):
        self._all_policies = self._create_all_policies()
        self.enabled_policies = []


    def _create_all_policies(self):
        # See the docstring of import_all_policies
        # 1st step
        import_all_policies()

        # 2nd step
        policy_class_map = get_policy_class_map()

        # 3rd step
        policy_map = dict([(policy_name, PolicyClass())
                           for policy_name, PolicyClass
                           in policy_class_map.items()])

        return policy_map


    def _is_policy_exists(self, name):
        return name in self._all_policies


    def _get_policy(self, name):
        return self._all_policies[name]


    def _warn_unexistent_policy(self, policy_name):
        logging.warning('Policy `{name}` is not defined'.format(
            name=policy_name))


    def update_by_config(self, policy_enabling_map):
        """ Update policies set by the policy enabling map.

        Expect the policy_enabling_map structure to be (represented by YAML):
            - PolicyFoo:
              enabled: True
            - PolicyBar:
              enabled: False
              additional_field: 'is_ok'
        """
        self.enabled_policies = []

        for policy_name, policy_config in policy_enabling_map.items():
            if not self._is_policy_exists(policy_name):
                self._warn_unexistent_policy(policy_name)
                continue

            if policy_config['enabled']:
                enabled_policy = self._get_policy(policy_name)
                self.enabled_policies.append(enabled_policy)


    def get_enabled_policies(self):
        """ Returns enabled policies. """
        return self.enabled_policies


def import_all_policies():
    """ Import all policies that were registered by vint.linting.policy_loader.

    Dynamic policy importing is comprised of the 3 steps
      1. Try to import all policy modules (then we can't know what policies exist)
      2. In policy module, register itself by using vint.linting.policy_loader
      3. After all policies registered by itself, we can get policy classes
    """
    pkg_name = _get_policy_package_name_for_test()
    pkg_path_list = pkg_name.split('.')

    # TODO: Fix policy loading mechanism. It seems too fragile and complex.
    pkg_path = str(Path(_get_vint_root(), *pkg_path_list).resolve())

    for loader, module_name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if not is_pkg:
            module_fqn = pkg_name + '.' + module_name
            logging.info('Loading the policy module `{fqn}`'.format(fqn=module_fqn))
            importlib.import_module(module_fqn)


def _get_vint_root():
    return Path(__file__).parent.parent.parent


def _get_policy_package_name_for_test():
    """ Test hook method that returns a package name for policy modules. """
    return 'vint.linting.policy'
