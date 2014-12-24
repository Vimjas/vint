import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_set_nocompatible import ProhibitSetNoCompatible


INVALID_VIM_SCRIPT = get_fixture_path(
    'prohibit_set_nocompatible_invalid.vim'
)
INVALID_VIM_SCRIPT_WITH_ABBREVIATION = get_fixture_path(
    'prohibit_set_nocompatible_invalid_with_abbreviation.vim'
)
VALID_VIM_SCRIPT = get_fixture_path(
    'prohibit_set_nocompatible_valid.vim'
)


class TestProhibitSetNoCompatible(PolicyAssertion, unittest.TestCase):
    def create_violation(self, line_number, path):
        return {
            'name': 'ProhibitSetNoCompatible',
            'level': Level.WARNING,
            'position': {
                'line': line_number,
                'column': 1,
                'path': path
            }
        }


    def test_get_violation_if_found_with_valid(self):
        self.assertFoundNoViolations(VALID_VIM_SCRIPT,
                                     ProhibitSetNoCompatible)


    def test_get_violation_if_found_with_invalid_file(self):
        expected_violations = [
            self.create_violation(1, INVALID_VIM_SCRIPT),
        ]
        self.assertFoundViolationsEqual(INVALID_VIM_SCRIPT,
                                        ProhibitSetNoCompatible,
                                        expected_violations)


    def test_get_violation_if_found_with_invalid_file_with_abbreviation(self):
        expected_violations = [
            self.create_violation(1, INVALID_VIM_SCRIPT_WITH_ABBREVIATION),
        ]
        self.assertFoundViolationsEqual(INVALID_VIM_SCRIPT_WITH_ABBREVIATION,
                                        ProhibitSetNoCompatible,
                                        expected_violations)


if __name__ == '__main__':
    unittest.main()
