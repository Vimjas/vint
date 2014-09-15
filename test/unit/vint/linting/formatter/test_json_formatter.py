import unittest
from test.asserting.formatter import FormatterAssertion

import json
from pathlib import Path
from vint.linting.formatter.json_formatter import JSONFormatter
from vint.linting.level import Level


class TestJSONFormatter(FormatterAssertion, unittest.TestCase):
    def test_format_violations(self):
        cmdargs = {}
        formatter = JSONFormatter(cmdargs)

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

        expected_output = [
            {
                'policy_name': 'ProhibitSomethingEvil',
                'severity': 'warning',
                'description': 'this code is tooooo evil',
                'reference': 'me',
                'line_number': 1,
                'column_number': 2,
                'file_path': str(Path('path', 'to', 'file1')),
            },
            {
                'policy_name': 'ProhibitSomethingDangerous',
                'severity': 'warning',
                'description': 'this code is tooooo dangerous',
                'reference': 'you',
                'line_number': 11,
                'column_number': 21,
                'file_path': str(Path('path', 'to', 'file2')),
            },
        ]

        json_output = formatter.format_violations(violations)
        parsed_output = json.loads(json_output)

        self.maxDiff = 1500
        self.assertEqual(parsed_output, expected_output)


if __name__ == '__main__':
    unittest.main()
