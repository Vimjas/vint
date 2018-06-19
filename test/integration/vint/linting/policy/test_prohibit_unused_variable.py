import unittest
import enum
from test.asserting.policy import PolicyAssertion, get_fixture_path
from vint.linting.level import Level
from vint.linting.policy.prohibit_unused_variable import ProhibitUnusedVariable

class Fixtures(enum.Enum):
    VALID_VIM_SCRIPT = get_fixture_path('prohibit_unused_variable_valid.vim')
    INVALID_VIM_SCRIPT = get_fixture_path('prohibit_unused_variable_invalid.vim')
    ISSUE_274 = get_fixture_path('prohibit_unused_variable_issue_274.vim')
    IGNORED_PATTERNS = get_fixture_path('prohibit_unused_variable_ignored_patterns.vim')
    README = get_fixture_path('prohibit_unused_variable_readme.vim')


class TestProhibitUnusedVariable(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(Fixtures.VALID_VIM_SCRIPT.value,
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
            self.create_violation(2, 5, Fixtures.INVALID_VIM_SCRIPT.value),
            self.create_violation(4, 11, Fixtures.INVALID_VIM_SCRIPT.value),
            self.create_violation(7, 25, Fixtures.INVALID_VIM_SCRIPT.value),
            self.create_violation(7, 36, Fixtures.INVALID_VIM_SCRIPT.value),
            self.create_violation(11, 9, Fixtures.INVALID_VIM_SCRIPT.value),
            self.create_violation(12, 9, Fixtures.INVALID_VIM_SCRIPT.value),
            self.create_violation(15, 8, Fixtures.INVALID_VIM_SCRIPT.value),
        ]

        self.assertFoundViolationsEqual(Fixtures.INVALID_VIM_SCRIPT.value,
                                        ProhibitUnusedVariable,
                                        expected_violations)

    def test_issue_274(self):
        self.assertFoundNoViolations(Fixtures.ISSUE_274.value, ProhibitUnusedVariable)


    def test_ignored_patterns(self):
        expected_violations = [
            self.create_violation(1, 5, Fixtures.IGNORED_PATTERNS.value),
        ]

        self.assertFoundViolationsEqual(Fixtures.IGNORED_PATTERNS.value,
                                        ProhibitUnusedVariable,
                                        expected_violations,
                                        policy_options={'ignored_patterns': ['_ignored$']})


    def test_readme(self):
        self.assertFoundNoViolations(Fixtures.README.value,
                                     ProhibitUnusedVariable)


if __name__ == '__main__':
    unittest.main()
