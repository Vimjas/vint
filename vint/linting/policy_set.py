import logging
from vint.linting.level import is_level_enabled
import vint.linting.policy_registry as policy_registry


class PolicySet(object):
    def __init__(self, policy_classes):
        self._all_policies_map = PolicySet.create_all_policies_map(policy_classes)
        self.enabled_policies = []


    @classmethod
    def create_all_policies_map(cls, policy_classes):
        policy_map = {PolicyClass.__name__: PolicyClass() for PolicyClass in policy_classes}

        return policy_map


    def _is_policy_exists(self, name):
        return name in self._all_policies_map


    def _get_policy(self, name):
        return self._all_policies_map[name]


    def _warn_unexistent_policy(self, policy_name):
        logging.warning('Policy `{name}` is not defined'.format(
            name=policy_name))


    def _get_enabling_map(self, config_dict):
        severity = config_dict['cmdargs']['severity']
        policy_enabling_map = {}

        for policy_name, policy in self._all_policies_map.items():
            policy_enabling_map[policy_name] = is_level_enabled(policy.level, severity)

        prior_policy_enabling_map = config_dict['policies']

        for policy_name, policy in prior_policy_enabling_map.items():
            if 'enabled' in policy:
                policy_enabling_map[policy_name] = policy['enabled']

        return policy_enabling_map


    def update_by_config(self, config_dict):
        """ Update policies set by the config dictionary.

        Expect the policy_enabling_map structure to be (represented by YAML):
            - PolicyFoo:
              enabled: True
            - PolicyBar:
              enabled: False
              additional_field: 'is_ok'
        """
        policy_enabling_map = self._get_enabling_map(config_dict)
        self.enabled_policies = []

        for policy_name, is_policy_enabled in policy_enabling_map.items():
            if not self._is_policy_exists(policy_name):
                self._warn_unexistent_policy(policy_name)
                continue

            if is_policy_enabled:
                enabled_policy = self._get_policy(policy_name)
                self.enabled_policies.append(enabled_policy)


    def get_enabled_policies(self):
        """ Returns enabled policies. """
        return self.enabled_policies
