import unittest
import os.path
from itertools import zip_longest
from vint.linting.linter import Linter


class PolicyAssertion(unittest.TestCase):
    class PolicySetPassThrough(object):
        def __init__(self, *policies):
            self._policies = policies


        def get_enabled_policies(self):
            return self._policies


        def update_by_config(self, policy_enabling_map):
            pass


    class ConfigPassThrough(object):
        def __init__(self, policy_names_to_enable):

            policy_enabling_map = dict((policy_name, {'enabled': True})
                                       for policy_name in policy_names_to_enable)

            self._config_dict = {
                'policies': policy_enabling_map
            }


        def append_config_source(self, config_source):
            # Ignore a comment config source
            pass


        def get_config_dict(self):
            return self._config_dict


    def assertFoundViolationsEqual(self, path, Policy, expected_violations):
        policy_to_test = Policy()
        policy_name = Policy.__name__

        policy_set = PolicyAssertion.PolicySetPassThrough(policy_to_test)
        config = PolicyAssertion.ConfigPassThrough(policy_name)

        linter = Linter(policy_set, config.get_config_dict())

        violations = linter.lint(path)

        for violation, expected_violation in zip_longest(violations, expected_violations):
            self.assertViolation(violation, expected_violation)


    def assertViolation(self, actual_violation, expected_violation):
        self.assertIsNot(actual_violation, None)
        self.assertIsNot(expected_violation, None)

        self.assertEqual(actual_violation['name'], expected_violation['name'])
        self.assertEqual(actual_violation['position'], expected_violation['position'])
        self.assertEqual(actual_violation['level'], expected_violation['level'])

        self.assertIsInstance(actual_violation['description'], str)


def get_fixture_path(filename):
    return os.path.join('test', 'fixture', 'policy', filename)
