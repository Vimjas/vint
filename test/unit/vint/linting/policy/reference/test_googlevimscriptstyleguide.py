import unittest
from vint.linting.policy.reference.googlevimscriptstyleguide import get_reference_source


class TestGoogleVimScriptStyleGuide(unittest.TestCase):
    def test_get_reference_source(self):
        actual_ref_source = get_reference_source('STRINGS')
        expected_ref_source = 'Google VimScript Style Guide (Strings)'

        self.assertEqual(actual_ref_source, expected_ref_source)

if __name__ == '__main__':
    unittest.main()
