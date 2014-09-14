import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_no_abort_function import ProhibitNoAbortFunction

PATH_VALID_VIM_SCRIPT_1 = get_fixture_path('prohibit_no_abort_function_valid.vim')
PATH_VALID_VIM_SCRIPT_2 = get_fixture_path('autoload', 'prohibit_no_abort_function_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('autoload', 'prohibit_no_abort_function_invalid.vim')


class TestProhibitNoAbortFunction(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT_1,
                                     ProhibitNoAbortFunction)


    def test_get_violation_if_found_when_file_is_valid_out_of_autoload(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT_2,
                                     ProhibitNoAbortFunction)


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            {
                'name': 'ProhibitNoAbortFunction',
                'level': Level.WARNING,
                'position': {
                    'line': 1,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitNoAbortFunction',
                'level': Level.WARNING,
                'position': {
                    'line': 4,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitNoAbortFunction',
                'level': Level.WARNING,
                'position': {
                    'line': 7,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitNoAbortFunction,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
