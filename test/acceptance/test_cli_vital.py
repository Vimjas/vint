import unittest
from pathlib import Path
import subprocess


class TestVintDoNotDiedWhenLintingVital(unittest.TestCase):
    def assertVintStillAlive(self, cmd):
        try:
            got_output = subprocess.check_output(cmd,
                                                 stderr=subprocess.STDOUT,
                                                 universal_newlines=True)
        except subprocess.CalledProcessError as err:
            got_output = err.output

        unexpected_keyword = r'^Traceback'
        self.assertNotRegex(got_output, unexpected_keyword)


    def assertNotRegex(self, string, pattern):
        assertNotRegexpMatches = getattr(self, 'assertNotRegexpMatches', None)
        if assertNotRegexpMatches:
            assertNotRegexpMatches(string, pattern)
            return

        super(TestVintDoNotDiedWhenLintingVital, self).assertNotRegex(string, pattern)



    def test_not_died_when_linting_vital(self):
        vital_dir = str(Path('test', 'fixture', 'cli', 'vital.vim'))
        cmd = ['vint', vital_dir]

        self.assertVintStillAlive(cmd)


if __name__ == '__main__':
    unittest.main()
