import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_missing_scriptencoding import ProhibitMissingScriptEncoding


NO_MULTI_BYTE_CHAR_VIM_SCRIPT = get_fixture_path('prohibit_missing_scriptencoding_valid_no_multibyte_char.vim')
SCRIPT_ENCODING_VIM_SCRIPT = get_fixture_path('prohibit_missing_scriptencoding_valid_scriptencoding.vim')
INVALID_VIM_SCRIPT = get_fixture_path('prohibit_missing_scriptencoding_invalid.vim')


class TestProhibitMissingScriptEncoding(PolicyAssertion, unittest.TestCase):
    def _create_violation_by_line_number(self, line_number):
        return {
            'name': 'ProhibitMissingScriptEncoding',
            'level': Level.WARNING,
            'position': {
                'line': line_number,
                'column': 1,
                'path': INVALID_VIM_SCRIPT
            }
        }


    def test_get_violation_if_found_with_valid_file_no_multibyte_char(self):
        self.assertFoundNoViolations(NO_MULTI_BYTE_CHAR_VIM_SCRIPT,
                                     ProhibitMissingScriptEncoding)


    def test_get_violation_if_found_with_valid_file_scriptencoding(self):
        self.assertFoundNoViolations(SCRIPT_ENCODING_VIM_SCRIPT,
                                     ProhibitMissingScriptEncoding)


    def test_get_violation_if_found_with_invalid_file(self):
        expected_violations = [
            {
                'name': 'ProhibitMissingScriptEncoding',
                'level': Level.WARNING,
                'position': {
                    'line': 1,
                    'column': 1,
                    'path': INVALID_VIM_SCRIPT
                },
            },
        ]
        self.assertFoundViolationsEqual(INVALID_VIM_SCRIPT,
                                        ProhibitMissingScriptEncoding,
                                        expected_violations)


if __name__ == '__main__':
    unittest.main()
