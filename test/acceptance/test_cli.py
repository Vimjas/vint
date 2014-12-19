import unittest
from pathlib import Path
import json
import subprocess


class TestCLI(unittest.TestCase):
    def assertRegex(self, string, pattern):
        assertRegexpMatches = getattr(self, 'assertRegexpMatches', None)
        if assertRegexpMatches:
            assertRegexpMatches(string, pattern)
            return

        super(TestCLI, self).assertRegex(string, pattern)


    def test_exec_vint_with_valid_file_on_project_root(self):
        valid_file = str(Path('test', 'fixture', 'cli', 'valid1.vim'))
        cmd = ['vint', valid_file]

        got_output = subprocess.check_output(cmd, universal_newlines=True)

        expected_output = ''
        self.assertEqual(got_output, expected_output)


    def test_exec_vint_with_invalid_file_on_project_root(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = ['vint', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = '{file_path}:1:13:'.format(file_path=invalid_file)
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_no_args(self):
        cmd = ['vint']

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = r'^vint ERROR:'
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_unexistent_file(self):
        cmd = ['vint', '/path/to/unexistent']

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = r'^vint ERROR:'
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_stat_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = ['vint', '--stat', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = '{file_path}:1:13:'.format(file_path=invalid_file)
        expected_stat_pattern = 'Total'
        self.assertRegex(got_output, expected_output_pattern)
        self.assertRegex(got_output, expected_stat_pattern)


    def test_exec_vint_with_json_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = ['vint', '--json', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            # We should not capture STRERR because coverage plugin use it.
            subprocess.check_output(cmd,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        print(got_output)
        self.assertIsInstance(json.loads(got_output), list)


    def test_exec_vint_with_verbose_flag(self):
        valid_file = str(Path('test', 'fixture', 'cli', 'valid1.vim'))
        cmd = ['vint', '--verbose', valid_file]

        got_output = subprocess.check_output(cmd,
                                             universal_newlines=True,
                                             stderr=subprocess.STDOUT)

        expected_output_pattern = r'^vint INFO:'
        self.assertRegex(got_output, expected_output_pattern)


    @unittest.skip('Does drone.io not like ANSI color?')
    def test_exec_vint_with_color_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = ['vint', '--color', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = '\\033\['
        self.assertRegex(got_output, expected_output_pattern)


if __name__ == '__main__':
    unittest.main()
