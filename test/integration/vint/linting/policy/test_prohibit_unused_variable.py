import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_unused_variable import ProhibitUnusedVariable

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_unused_variable_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_unused_variable_invalid.vim')
PATH_ISSUE_274 = get_fixture_path('prohibit_unused_variable_issue_274.vim')
PATH_IGNORED_PATTERNS = get_fixture_path('prohibit_unused_variable_ignored_patterns.vim')


class TestProhibitUnusedVariable(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitUnusedVariable)


    def create_violation(self, line, column, path):
        return {
            'name': 'ProhibitUnusedVariable',
            'level': Level.WARNING,
            'position': {
                'line': line,
                'column': column,
                'path': path
            }
        }


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            self.create_violation(2, 5, PATH_INVALID_VIM_SCRIPT),
            self.create_violation(4, 11, PATH_INVALID_VIM_SCRIPT),
            self.create_violation(7, 25, PATH_INVALID_VIM_SCRIPT),
            self.create_violation(7, 36, PATH_INVALID_VIM_SCRIPT),
            self.create_violation(11, 9, PATH_INVALID_VIM_SCRIPT),
            self.create_violation(12, 9, PATH_INVALID_VIM_SCRIPT),
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitUnusedVariable,
                                        expected_violations)

    def test_issue_274(self):
        self.assertFoundNoViolations(PATH_ISSUE_274, ProhibitUnusedVariable)


    def test_ignored_patterns(self):
        expected_violations = [
            self.create_violation(1, 5, PATH_IGNORED_PATTERNS),
        ]

        self.assertFoundViolationsEqual(PATH_IGNORED_PATTERNS,
                                        ProhibitUnusedVariable,
                                        expected_violations,
                                        policy_options={'ignored_patterns': ['_ignored$']})


if __name__ == '__main__':
    unittest.main()
