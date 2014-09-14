import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_unnecessary_double_quote import ProhibitUnnecessaryDoubleQuote

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_unnecessary_double_quote_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_unnecessary_double_quote_invalid.vim')


class TestProhibitUnnecessaryDoubleQuote(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitUnnecessaryDoubleQuote)


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            {
                'name': 'ProhibitUnnecessaryDoubleQuote',
                'level': Level.WARNING,
                'position': {
                    'line': 2,
                    'column': 6,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUnnecessaryDoubleQuote',
                'level': Level.WARNING,
                'position': {
                    'line': 3,
                    'column': 6,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitUnnecessaryDoubleQuote,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
