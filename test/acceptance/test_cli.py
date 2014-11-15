import unittest
import os
from pathlib import Path
import json
import subprocess


class TestCLI(unittest.TestCase):
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
        self.assertRegexpMatches(got_output, expected_output_pattern)


    def test_exec_vint_with_no_args(self):
        cmd = ['vint']

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        self.assertTrue(got_output.startswith('vint error:'))


    def test_exec_vint_with_unexistent_file(self):
        cmd = ['vint', '/path/to/unexistent']

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        self.assertTrue(got_output.startswith('vint error:'))


    def test_exec_vint_with_json_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = ['vint', '--json', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        self.assertIsInstance(json.loads(got_output), list)


    @unittest.skip('Does drone.io not like ANSI color?')
    def test_exec_vint_with_color_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = ['vint', '--color', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = '\\033\['
        self.assertRegexpMatches(got_output, expected_output_pattern)


if __name__ == '__main__':
    unittest.main()
