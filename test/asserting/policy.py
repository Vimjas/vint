import unittest
from pathlib import Path
from pprint import pprint
from compat.itertools import zip_longest
from vint.linting.linter import Linter


class PolicyAssertion(unittest.TestCase):
    class StubPolicySet(object):
        def __init__(self, *policies):
            self._policies = policies


        def get_enabled_policies(self):
            return self._policies


        def update_by_config(self, policy_enabling_map):
            pass


    class StubConfigContainer(object):
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


    def assertFoundNoViolations(self, path, Policy):
        self.assertFoundViolationsEqual(path, Policy, [])


    def assertFoundViolationsEqual(self, path, Policy, expected_violations):
        policy_to_test = Policy()
        policy_name = Policy.__name__

        policy_set = PolicyAssertion.StubPolicySet(policy_to_test)
        config = PolicyAssertion.StubConfigContainer(policy_name)

        linter = Linter(policy_set, config.get_config_dict())
        violations = linter.lint_file(path)

        assert len(violations) == len(expected_violations)

        for violation, expected_violation in zip_longest(violations, expected_violations):
            self.assertViolation(violation, expected_violation)


    def assertViolation(self, actual_violation, expected_violation):
        self.assertIsNot(actual_violation, None)
        self.assertIsNot(expected_violation, None)

        pprint(actual_violation)

        self.assertEqual(actual_violation['name'], expected_violation['name'],
                         'Expected violation name was returned')
        self.assertEqual(actual_violation['position'], expected_violation['position'],
                         'Expected violation position was returned')
        self.assertEqual(actual_violation['level'], expected_violation['level'],
                         'Expected violation level was returned')

        self.assertIsInstance(actual_violation['description'], str)


def get_fixture_path(*filename):
    return Path('test', 'fixture', 'policy', *filename)
