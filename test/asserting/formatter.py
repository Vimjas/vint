import unittest


class FormatterAssertion(unittest.TestCase):
    def assertFormattedViolations(self, formatter, violations, expected_output):
        got_output = formatter.format_violations(violations)
        self.assertEqual(got_output, expected_output)
