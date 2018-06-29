import unittest
from pathlib import Path
from pprint import pprint
from vint.compat.itertools import zip_longest
from vint.linting.policy_set import PolicySet
from vint.linting.linter import Linter
from vint.linting.level import Level


class PolicyAssertion(unittest.TestCase):
    def assertFoundNoViolations(self, path, Policy, policy_options=None):
        self.assertFoundViolationsEqual(path, Policy, [], policy_options)


    def assertFoundViolationsEqual(self, path, Policy, expected_violations, policy_options=None):
        policy_name = Policy.__name__
        policy_set = PolicySet([Policy])

        config_dict = {
            'cmdargs': {
                'severity': Level.STYLE_PROBLEM,
            },
            'policies': {
                policy_name: {
                    'enabled': True,
                }
            },
        }

        if policy_options is not None:
            config_dict['policies'][policy_name] = policy_options

        linter = Linter(policy_set, config_dict)
        violations = linter.lint_file(path)

        pprint(violations)
        self.assertEqual(len(violations), len(expected_violations))

        for violation, expected_violation in zip_longest(violations, expected_violations):
            self.assertViolation(violation, expected_violation)


    def assertViolation(self, actual_violation, expected_violation):
        self.assertIsNot(actual_violation, None)
        self.assertIsNot(expected_violation, None)
        self.assertEqual(actual_violation['name'], expected_violation['name'])
        self.assertEqual(actual_violation['position'], expected_violation['position'])
        self.assertEqual(actual_violation['level'], expected_violation['level'])
        self.assertIsInstance(actual_violation['description'], str)


def get_fixture_path(*filename):
    return Path('test', 'fixture', 'policy', *filename)
