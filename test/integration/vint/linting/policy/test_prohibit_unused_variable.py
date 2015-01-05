import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_unused_variable import ProhibitUnusedVariable

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_unused_variable_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_unused_variable_invalid.vim')


class TestProhibitUnusedVariable(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitUnusedVariable)


    def create_violation(self, line, column):
        return {
            'name': 'ProhibitUnusedVariable',
            'level': Level.WARNING,
            'position': {
                'line': line,
                'column': column,
                'path': PATH_INVALID_VIM_SCRIPT
            }
        }


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            self.create_violation(2, 5),
            self.create_violation(4, 11),
            self.create_violation(7, 25),
            self.create_violation(7, 36),
            self.create_violation(11, 9),
            self.create_violation(12, 9),
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitUnusedVariable,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
