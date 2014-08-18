import unittest
import os.path
from itertools import zip_longest
from vint.linting.linter import Linter


class PolicyAssertion(unittest.TestCase):
    def assertFoundViolationsEqual(self, path, Policy, expected_violations):
        linter = Linter([Policy()])
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
