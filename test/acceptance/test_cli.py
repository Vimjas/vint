import unittest
from pathlib import Path
import json
import subprocess
import sys


class TestCLI(unittest.TestCase):
    if sys.version_info <= (3,):
        def assertRegex(self, string, pattern):
            return super(TestCLI, self).assertRegexpMatches(string, pattern)


    def assertReturnedStdoutEqual(self, expected_stdout, args):
        got_stdout = '(no stdout)'
        cmd = [sys.executable, '-m', 'vint'] + args
        try:
            got_stdout = subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            print('Got stderr: `{err_message}`'.format(err_message=err))
        finally:
            print('Got stdout: `{stdout}`'.format(stdout=got_stdout))

        self.assertEqual(expected_stdout, got_stdout)


    def test_exec_vint_with_valid_file_on_project_root(self):
        valid_file = str(Path('test', 'fixture', 'cli', 'valid1.vim'))

        expected_output = ''

        self.assertReturnedStdoutEqual(expected_output, [valid_file])


    def test_exec_vint_with_valid_file_encoded_cp932_on_project_root(self):
        valid_file = str(Path('test', 'fixture', 'cli', 'valid-cp932.vim'))

        expected_output = ''

        self.assertReturnedStdoutEqual(expected_output, [valid_file])


    def test_exec_vint_with_invalid_file_on_project_root(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = [sys.executable, '-m', 'vint', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = '{file_path}:1:13:'.format(file_path=invalid_file)
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_no_args(self):
        cmd = [sys.executable, '-m', 'vint']

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = r'^vint ERROR:'
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_unexistent_file(self):
        cmd = [sys.executable, '-m', 'vint', '/path/to/unexistent']

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = r'^vint ERROR:'
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_stat_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = [sys.executable, '-m', 'vint', '--stat', invalid_file]

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
        cmd = [sys.executable, '-m', 'vint', '--json', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            # We should not capture STRERR because coverage plugin use it.
            subprocess.check_output(cmd,
                                    universal_newlines=True)

        got_output = context_manager.exception.output

        print(got_output)
        self.assertIsInstance(json.loads(got_output), list)


    def test_exec_vint_with_verbose_flag(self):
        valid_file = str(Path('test', 'fixture', 'cli', 'valid1.vim'))
        cmd = [sys.executable, '-m', 'vint', '--verbose', valid_file]

        got_output = subprocess.check_output(cmd,
                                             universal_newlines=True,
                                             stderr=subprocess.STDOUT)

        expected_output_pattern = r'^vint DEBUG:'
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_color_flag(self):
        invalid_file = str(Path('test', 'fixture', 'cli', 'invalid1.vim'))
        cmd = [sys.executable, '-m', 'vint', '--color', invalid_file]

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = r'\033\['
        self.assertRegex(got_output, expected_output_pattern)


    def test_exec_vint_with_pipe(self):
        cmd = 'echo "foo" =~ "bar" | bin/vint --stdin-display-name STDIN_TEST -'

        with self.assertRaises(subprocess.CalledProcessError) as context_manager:
            subprocess.check_output(cmd, shell=True, universal_newlines=True)

        got_output = context_manager.exception.output

        expected_output_pattern = '^STDIN_TEST:'
        self.assertRegex(got_output, expected_output_pattern)


if __name__ == '__main__':
    unittest.main()
