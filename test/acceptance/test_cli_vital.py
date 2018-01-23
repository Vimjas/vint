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

        unexpected_keyword = 'Traceback'
        self.assertFalse(unexpected_keyword in got_output,
                         'vint was died when linting vital.vim: ' + got_output)


    def test_survive_after_linting(self):
        vital_dir = str(Path('test', 'fixture', 'cli', 'vital.vim'))
        cmd = ['bin/vint', vital_dir]

        self.assertVintStillAlive(cmd)


if __name__ == '__main__':
    unittest.main()
