import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_implicit_scope_builtin_variable import (
    ProhibitImplicitScopeBuiltinVariable,
)

PATH_VALID_VIM_SCRIPT = get_fixture_path(
    'prohibit_implicit_scope_builtin_variable_valid.vim')
PATH_INVALID_VIM_SCRIPT = get_fixture_path(
    'prohibit_implicit_scope_builtin_variable_invalid.vim')


class TestProhibitImplicitScopeBuiltinVariable(PolicyAssertion, unittest.TestCase):
    def test_get_violation_if_found_when_file_is_valid(self):
        self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT,
                                     ProhibitImplicitScopeBuiltinVariable)


    def create_violation(self, line, column):
        return {
            'name': 'ProhibitImplicitScopeBuiltinVariable',
            'level': Level.WARNING,
            'position': {
                'line': line,
                'column': column,
                'path': PATH_INVALID_VIM_SCRIPT
            }
        }


    def test_get_violation_if_found_when_file_is_invalid(self):
        expected_violations = [
            self.create_violation(4, 9),
            self.create_violation(5, 10),
        ]

        self.assertFoundViolationsEqual(PATH_INVALID_VIM_SCRIPT,
                                        ProhibitImplicitScopeBuiltinVariable,
                                        expected_violations)

if __name__ == '__main__':
    unittest.main()
