import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_command_rely_on_user import ProhibitCommandRelyOnUser

PATH_VALID_VIM_SCRIPT = get_fixture_path('prohibit_command_rely_on_user_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path('prohibit_command_rely_on_user_invalid.vim')


class TestProhibitCommandRelyOnUser(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitCommandRelyOnUser)


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            {
                'name': 'ProhibitCommandRelyOnUser',
                'level': Level.WARNING,
                'position': {
                    'line': 1,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitCommandRelyOnUser',
                'level': Level.WARNING,
                'position': {
                    'line': 2,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitCommandRelyOnUser',
                'level': Level.WARNING,
                'position': {
                    'line': 3,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitCommandRelyOnUser',
                'level': Level.WARNING,
                'position': {
                    'line': 4,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'ProhibitCommandRelyOnUser',
                'level': Level.WARNING,
                'position': {
                    'line': 5,
                    'column': 1,
                    'path': PATH_INVALID_VIM_SCRIPT
                },
            },
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitCommandRelyOnUser,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
