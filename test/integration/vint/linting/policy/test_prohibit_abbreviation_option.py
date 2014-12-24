import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_abbreviation_option import ProhibitAbbreviationOption

VALID_VIM_SCRIPT = get_fixture_path('prohibit_abbreviation_option_valid.vim')
INVALID_SET_VIM_SCRIPT = get_fixture_path('prohibit_abbreviation_option_invalid_with_set.vim')
INVALID_VAR_VIM_SCRIPT = get_fixture_path('prohibit_abbreviation_option_invalid_with_var.vim')


class TestProhibitAbbreviationOption(PolicyAssertion, unittest.TestCase):
    def create_violation(self, line_number, col_number, path):
        return {
            'name': 'ProhibitAbbreviationOption',
            'level': Level.STYLE_PROBLEM,
            'position': {
                'line': line_number,
                'column': col_number,
                'path': path,
            },
        }


    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(VALID_VIM_SCRIPT,
                                     ProhibitAbbreviationOption)


    def test_get_violation_if_found_when_file_is_invalid_with_set(self):
        expected_violations = [
            self.create_violation(1, 1, INVALID_SET_VIM_SCRIPT),
            self.create_violation(2, 1, INVALID_SET_VIM_SCRIPT),
            self.create_violation(3, 1, INVALID_SET_VIM_SCRIPT),
            self.create_violation(4, 1, INVALID_SET_VIM_SCRIPT),
            self.create_violation(5, 1, INVALID_SET_VIM_SCRIPT),
        ]

        self.assertFoundViolationsEqual(INVALID_SET_VIM_SCRIPT,
                                        ProhibitAbbreviationOption,
                                        expected_violations)


    def test_get_violation_if_found_when_file_is_invalid_with_var(self):
        expected_violations = [
            self.create_violation(1, 18, INVALID_VAR_VIM_SCRIPT),
            self.create_violation(2, 5, INVALID_VAR_VIM_SCRIPT),
        ]

        self.assertFoundViolationsEqual(INVALID_VAR_VIM_SCRIPT,
                                        ProhibitAbbreviationOption,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
