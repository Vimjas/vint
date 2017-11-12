import unittest
from vint.ast.dictionary.autocmd_events import is_autocmd_event


class TestAutocmdEvent(unittest.TestCase):
    def test_is_autocmd_event(self):
        test_cases = [
            ('BufReadPost', True),
            ('FileType', True),
            ('FILETYPE', True),
            ('filetype', True),
            ('*', True),
            ('INVALID', False),
        ]

        for (event_name, expected) in test_cases:
            self.assertEqual(
                is_autocmd_event(event_name),
                expected,
                msg="{event_name} should be {expected}".format(event_name=event_name, expected=expected)
            )


if __name__ == '__main__':
    unittest.main()
