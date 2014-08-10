import unittest
from test.asserting.policy import PolicyAssertion
from test.asserting.policy import get_fixture_path

from lib.linting.level import Levels
from lib.linting.policy.prohibitunnecessarydoublequote import ProhibitUnnecessaryDoubleQuote

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_unnecessary_double_quote_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_unnecessary_double_quote_invalid.vim')


class TestProhibitUnnecessaryDoubleQuote(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found(self):
        # Expect no violations found
        self.assertFoundViolationsEqual(PATH_VALID_VIM_SCRIPT, ProhibitUnnecessaryDoubleQuote, [])

        expected_violations = [
            {
                'name': 'ProhibitUnnecessaryDoubleQuote',
                'level': Levels['WARNING'],
                'position': {
                    'line': 2,
                    'column': 6,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitUnnecessaryDoubleQuote',
                'level': Levels['WARNING'],
                'position': {
                    'line': 3,
                    'column': 6,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT, ProhibitUnnecessaryDoubleQuote, expected_violations)

if __name__ == '__main__':
    unittest.main()
