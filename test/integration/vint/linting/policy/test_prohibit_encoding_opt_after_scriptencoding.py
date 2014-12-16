import unittest
from test.asserting.policy import PolicyAssertion, get_fixture_path

from vint.linting.level import Level
from vint.linting.policy.prohibit_encoding_opt_after_scriptencoding import (
    ProhibitEncodingOptionAfterScriptEncoding,
)


VALID_ORDER_VIM_SCRIPT = get_fixture_path(
    'prohibit_encoding_opt_after_scriptencoding_valid.vim'
)
NO_ENCODING_OPT_VIM_SCRIPT = get_fixture_path(
    'prohibit_encoding_opt_after_scriptencoding_valid_no_encoding_opt.vim'
)
NO_SCRIPT_ENCODING_VIM_SCRIPT = get_fixture_path(
    'prohibit_encoding_opt_after_scriptencoding_valid_no_scriptencoding.vim'
)
INVALID_ORDER_VIM_SCRIPT = get_fixture_path(
    'prohibit_encoding_opt_after_scriptencoding_invalid.vim'
)


class TestProhibitEncodingOptionAfterScriptEncoding(PolicyAssertion, unittest.TestCase):
    def _create_violation_by_line_number(self, line_number):
        return {
            'name': 'ProhibitEncodingOptionAfterScriptEncoding',
            'level': Level.WARNING,
            'position': {
                'line': line_number,
                'column': 1,
                'path': INVALID_ORDER_VIM_SCRIPT
            }
        }


    def test_get_violation_if_found_with_valid_file(self):
        self.assertFoundNoViolations(VALID_ORDER_VIM_SCRIPT,
                                     ProhibitEncodingOptionAfterScriptEncoding)


    def test_get_violation_if_found_with_valid_file_no_encoding_option(self):
        self.assertFoundNoViolations(NO_ENCODING_OPT_VIM_SCRIPT,
                                     ProhibitEncodingOptionAfterScriptEncoding)


    def test_get_violation_if_found_with_valid_file_no_scriptencoding(self):
        self.assertFoundNoViolations(NO_SCRIPT_ENCODING_VIM_SCRIPT,
                                     ProhibitEncodingOptionAfterScriptEncoding)


    def test_get_violation_if_found_with_invalid_file(self):
        expected_violations = [self._create_violation_by_line_number(2)]

        self.assertFoundViolationsEqual(INVALID_ORDER_VIM_SCRIPT,
                                        ProhibitEncodingOptionAfterScriptEncoding,
                                        expected_violations)


if __name__ == '__main__':
    unittest.main()
