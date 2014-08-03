import unittest
from lib.policy.reference.googlevimscriptstyleguide import get_reference_source


class TestGoogleVimScriptStyleGuide(unittest.TestCase):
    def test_get_reference_source(self):
        actual_ref_source = get_reference_source('STRINGS')
        expected_ref_source = 'Section `Strings` at Google VimScript Style Guide'

        self.assertEqual(actual_ref_source, expected_ref_source)

if __name__ == '__main__':
    unittest.main()
