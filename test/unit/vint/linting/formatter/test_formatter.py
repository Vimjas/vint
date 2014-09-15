import unittest
from pathlib import Path
from test.asserting.formatter import FormatterAssertion
from vint.linting.formatter.formatter import Formatter
from vint.linting.level import Level


class TestFormatter(FormatterAssertion, unittest.TestCase):
    def test_format_violations_with_format_option(self):
        config_dict = {
            'cmdargs': {
                'format': '{file_name}|{file_path}|{line_number}|{column_number}|{severity}|{description}|{policy_name}|{reference}'
            }
        }
        formatter = Formatter(config_dict)

        violations = [
            {
                'name': 'ProhibitSomethingEvil',
                'level': Level.WARNING,
                'description': 'this code is tooooo evil',
                'reference': 'me',
                'position': {
                    'line': 1,
                    'column': 2,
                    'path': Path('path', 'to', 'file1')
                },
            },
            {
                'name': 'ProhibitSomethingDangerous',
                'level': Level.WARNING,
                'description': 'this code is tooooo dangerous',
                'reference': 'you',
                'position': {
                    'line': 11,
                    'column': 21,
                    'path': Path('path', 'to', 'file2')
                },
            },
        ]

        expected_output = """\
file1|path/to/file1|1|2|warning|this code is tooooo evil|ProhibitSomethingEvil|me
file2|path/to/file2|11|21|warning|this code is tooooo dangerous|ProhibitSomethingDangerous|you\
"""

        self.assertFormattedViolations(formatter, violations, expected_output)


    def test_format_violations(self):
        config_dict = {}
        formatter = Formatter(config_dict)

        violations = [
            {
                'name': 'ProhibitSomethingEvil',
                'level': Level.WARNING,
                'description': 'this code is tooooo evil',
                'reference': 'me',
                'position': {
                    'line': 1,
                    'column': 2,
                    'path': Path('path', 'to', 'file1')
                },
            },
            {
                'name': 'ProhibitSomethingDangerous',
                'level': Level.WARNING,
                'description': 'this code is tooooo dangerous',
                'reference': 'you',
                'position': {
                    'line': 11,
                    'column': 21,
                    'path': Path('path', 'to', 'file2')
                },
            },
        ]

        expected_output = """\
path/to/file1:1:2: this code is tooooo evil (see me)
path/to/file2:11:21: this code is tooooo dangerous (see you)\
"""

        self.assertFormattedViolations(formatter, violations, expected_output)


if __name__ == '__main__':
    unittest.main()
