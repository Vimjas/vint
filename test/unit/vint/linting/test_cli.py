import unittest
from vint.compat.unittest import mock

from vint.linting.cli import CLI
from vint.bootstrap import import_all_policies


class TestCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # For test_start_with_invalid_file_path.
        # The test case want to load saveral policies.
        import_all_policies()


    def assertExitWithSuccess(self, argv):
        with mock.patch('sys.argv', argv):
            with self.assertRaises(SystemExit) as e:
                cli = CLI()
                cli.start()

            self.assertEqual(e.exception.code, 0)


    def assertExitWithFailure(self, argv):
        with mock.patch('sys.argv', argv):
            with self.assertRaises(SystemExit) as e:
                cli = CLI()
                cli.start()

            self.assertNotEqual(e.exception.code, 0)


    def test_start_with_no_arg(self):
        argv = ['bin/vint']
        self.assertExitWithFailure(argv)


    def test_start_with_unexistent_file_path(self):
        argv = ['bin/vint', 'path/to/unexistent']
        self.assertExitWithFailure(argv)


    def test_start_with_valid_file_path(self):
        argv = ['bin/vint', 'test/fixture/cli/valid1.vim']
        self.assertExitWithSuccess(argv)


    def test_start_with_invalid_file_path(self):
        argv = ['bin/vint', 'test/fixture/cli/invalid1.vim']
        self.assertExitWithFailure(argv)


    def test_start_with_both_calid_invalid_file_paths(self):
        argv = ['bin/vint', 'test/fixture/cli/valid1.vim', 'test/fixture/cli/invalid1.vim']
        self.assertExitWithFailure(argv)


    @mock.patch('sys.stdin', open('test/fixture/cli/valid1.vim'))
    def test_passing_code_to_stdin_lints_the_code_from_stdin(self):
        argv = ['bin/vint', '-']
        self.assertExitWithSuccess(argv)

if __name__ == '__main__':
    unittest.main()
