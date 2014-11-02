import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_using_undeclared_variable import ProhibitUsingUndeclaredVariable

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_using_undeclared_variable_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_using_undeclared_variable_invalid.vim')


class TestProhibitUsingUndeclaredVariable(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitUsingUndeclaredVariable)


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 1,
                    'column': 6,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 5,
                    'column': 10,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 6,
                    'column': 10,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 10,
                    'column': 10,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 11,
                    'column': 10,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 12,
                    'column': 10,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 13,
                    'column': 10,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUsingUndeclaredVariable',
                'level': Level.WARNING,
                'position': {
                    'line': 16,
                    'column': 6,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitUsingUndeclaredVariable,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
