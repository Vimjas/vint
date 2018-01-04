import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_invalid_map_call import ProhibitInvalidMapCall

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_invalid_map_call_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_invalid_map_call_invalid.vim')


class TestProhibitInvalidMapCall(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_with_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT, ProhibitInvalidMapCall)


    def test_get_violation_if_found_with_invalid(self):
        expected_violations = [
            {
                'name': 'ProhibitInvalidMapCall',
                'level': Level.ERROR,
                'position': {
                    'line': 1,
                    'column': 16,
                    'path': PATH_INVALID_VIM_SCRIPT
                }
            }
        ]
        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitInvalidMapCall,
                                        expected_violations)
