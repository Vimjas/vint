import logging
from vint.linting.policy_registry import get_policy_class_map


class PolicySet(object):
    def __init__(self):
        self._all_policies = self._create_all_policies()
        self.enabled_policies = []


    def _create_all_policies(self):
        policy_class_map = get_policy_class_map()

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

            is_policy_enabled = policy_config['enabled']

            if is_policy_enabled:
                enabled_policy = self._get_policy(policy_name)
                self.enabled_policies.append(enabled_policy)

            self._log_policy_status(policy_name, is_policy_enabled)


    def get_enabled_policies(self):
        """ Returns enabled policies. """
        return self.enabled_policies


    def _log_policy_status(self, policy_name, enabled):
        status = 'enabled' if enabled else 'disabled'
        logging.debug('{status}: {policy_name}'.format(status=status,
                                                       policy_name=policy_name))
