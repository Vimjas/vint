import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_command_with_unintended_side_effect import ProhibitCommandWithUnintendedSideEffect

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_command_with_unintended_side_effect_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_command_with_unintended_side_effect_invalid.vim')


class TestProhibitCommandWithUnintendedSideEffect(PolicyAssertion, unittest.TestCase):
    def _create_violation_by_line_number(self, line_number):
        return {
            'name': 'ProhibitCommandWithUnintendedSideEffect',
            'level': Level.WARNING,
            'position': {
                'line': line_number,
                'column': 1,
                'path': PATH_INVALID_VIM_SCRIPT
            }
        }


    def test_get_violation_if_found_with_valid_file(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitCommandWithUnintendedSideEffect)


    def test_get_violation_if_found_with_invalid_file(self):
        expected_violations = [self._create_violation_by_line_number(line_number)
                               for line_number in range(1, 14)]

        # Offset range token length
        expected_violations[3]['position']['column'] = 2
        expected_violations[4]['position']['column'] = 6

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitCommandWithUnintendedSideEffect,
                                        expected_violations)


if __name__ == '__main__':
    unittest.main()
