import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_autocmd_with_no_group import ProhibitAutocmdWithNoGroup


VALID_VIM_SCRIPT_WITH_AUGROUP = get_fixture_path(
    'prohibit_autocmd_with_no_group_valid_with_augroup.vim'
)
VALID_VIM_SCRIPT_WITH_GROUP_PARAM = get_fixture_path(
    'prohibit_autocmd_with_no_group_valid_with_group_param.vim'
)
INVALID_VIM_SCRIPT = get_fixture_path(
    'prohibit_autocmd_with_no_group_invalid.vim'
)


class TestProhibitAutocmdWithNoGroup(PolicyAssertion, unittest.TestCase):
    def create_violation(self, line_number, path):
        return {
            'name': 'ProhibitAutocmdWithNoGroup',
            'level': Level.WARNING,
            'position': {
                'line': line_number,
                'column': 1,
                'path': path
            }
        }


    def test_get_violation_if_found_with_valid_file_with_augroup(self):
        self.assertFoundNoViolations(VALID_VIM_SCRIPT_WITH_AUGROUP,
                                     ProhibitAutocmdWithNoGroup)


    def test_get_violation_if_found_with_valid_file_with_group_param(self):
        self.assertFoundNoViolations(VALID_VIM_SCRIPT_WITH_GROUP_PARAM,
                                     ProhibitAutocmdWithNoGroup)


    def test_get_violation_if_found_with_invalid_file(self):
        expected_violations = [
            self.create_violation(1, INVALID_VIM_SCRIPT),
            self.create_violation(6, INVALID_VIM_SCRIPT),
            self.create_violation(7, INVALID_VIM_SCRIPT),
        ]
        self.assertFoundViolationsEqual(INVALID_VIM_SCRIPT,
                                        ProhibitAutocmdWithNoGroup,
                                        expected_violations)


if __name__ == '__main__':
    unittest.main()
