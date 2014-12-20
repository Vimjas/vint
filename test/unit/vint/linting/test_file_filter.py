import unittest
import os.path
from pathlib import Path
from vint.linting.file_filter import find_vim_script


FIXTURE_PATH_BASE = Path('test', 'fixture', 'file_filter')


def get_fixture_path(file_path):
    return Path(FIXTURE_PATH_BASE).joinpath(file_path)


class TestFileFilter(unittest.TestCase):
    def test_find_vim_script_by_given_no_file_paths(self):
        file_paths_to_find = []

        got_file_paths = map(str, find_vim_script(file_paths_to_find))

        expected_file_paths = []
        self.assertEqual(set(expected_file_paths), set(got_file_paths))


    def test_find_vim_script_by_given_a_file_path(self):
        file_paths_to_find = [
            get_fixture_path('1.vim'),
        ]

        got_file_paths = map(str, find_vim_script(file_paths_to_find))

        expected_file_paths = map(str, map(get_fixture_path, [
            '1.vim',
        ]))
        self.assertEqual(set(expected_file_paths), set(got_file_paths))


    def test_find_vim_script_by_given_nested_dir(self):
        file_paths_to_find = [
            FIXTURE_PATH_BASE,
        ]

        got_file_paths = map(str, find_vim_script(file_paths_to_find))

        expected_file_paths = map(str, map(get_fixture_path, [
            '.gvimrc',
            '.vimrc',
            '_gvimrc',
            '_vimrc',
            '1.vim',
            '2.vim',
            os.path.join('sub', '3.vim'),
            os.path.join('sub', '4.vim'),
        ]))
        self.assertEqual(set(expected_file_paths), set(got_file_paths))


    def test_find_vim_script_by_given_a_vim_script_unlinke_file_path(self):
        file_paths_to_find = [
            # We should pass through when given Vim script unlike file path.
            # It makes checking a file on user-dependent naming policy
            # convinience.
            get_fixture_path('not_vim_script'),
        ]

        got_file_paths = map(str, find_vim_script(file_paths_to_find))

        expected_file_paths = map(str, map(get_fixture_path, [
            'not_vim_script',
        ]))
        self.assertEqual(set(expected_file_paths), set(got_file_paths))


    def test_find_vim_script_by_given_several_vim_script(self):
        file_paths_to_find = [
            get_fixture_path('1.vim'),
            get_fixture_path('sub/3.vim'),
        ]

        got_file_paths = map(str, find_vim_script(file_paths_to_find))

        expected_file_paths = map(str, map(get_fixture_path, [
            '1.vim',
            'sub/3.vim',
        ]))
        self.assertEqual(set(expected_file_paths), set(got_file_paths))


if __name__ == '__main__':
    unittest.main()
