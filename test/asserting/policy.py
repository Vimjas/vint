import unittest
from pathlib import Path
from pprint import pprint
from vint.compat.itertools import zip_longest
from vint.linting.linter import Linter
from vint.linting.config.config_default_source import ConfigDefaultSource


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

            default_config_dict = ConfigDefaultSource(None).get_config_dict()
            policy_options = default_config_dict.get('policies', {})

            for policy, options in policy_options.items():
                options['enabled'] = False

            for policy in policy_names_to_enable:
                options = policy_options.setdefault(policy, {})
                options['enabled'] = True

            self._config_dict = {
                'policies': policy_options,
            }


        def append_config_source(self, config_source):
            # Ignore a comment config source
            pass


        def get_config_dict(self):
            return self._config_dict


    def assertFoundNoViolations(self, path, Policy, policy_options=None):
        self.assertFoundViolationsEqual(path, Policy, [], policy_options)


    def assertFoundViolationsEqual(self, path, Policy, expected_violations, policy_options=None):
        policy_to_test = Policy()
        policy_name = Policy.__name__

        policy_set = PolicyAssertion.StubPolicySet(policy_to_test)
        config = PolicyAssertion.StubConfigContainer(policy_name)

        if policy_options is not None:
            config.get_config_dict()['policies'][policy_name].update(policy_options)

        linter = Linter(policy_set, config.get_config_dict())
        violations = linter.lint_file(path)

        pprint(violations)
        self.assertEqual(len(violations), len(expected_violations))

        for violation, expected_violation in zip_longest(violations, expected_violations):
            self.assertViolation(violation, expected_violation)


    def assertViolation(self, actual_violation, expected_violation):
        self.assertIsNot(actual_violation, None)
        self.assertIsNot(expected_violation, None)

        pprint(actual_violation)

        assert actual_violation['name'] == expected_violation['name']
        assert actual_violation['position'] == expected_violation['position']
        assert actual_violation['level'] == expected_violation['level']

        self.assertIsInstance(actual_violation['description'], str)


def get_fixture_path(*filename):
    return Path('test', 'fixture', 'policy', *filename)
