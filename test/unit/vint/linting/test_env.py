import unittest
from unittest.mock import patch
from pathlib import Path
from vint.linting.env import build_environment

FIXTURE_PATH = Path('test', 'fixture', 'env')


class TestEnv(unittest.TestCase):
    def test_build_environment(self):
        cwd = Path('path', 'to', 'cwd')

        expected_env = {
            'cmdargs': {
                'files': [str(FIXTURE_PATH)],
                'verbose': True,
                'error': False,
                'warning': True,
                'style_problem': False,
                'max_violations': 10,
            },
            'file_paths': set([
                Path(FIXTURE_PATH, '1.vim'),
                Path(FIXTURE_PATH, '2.vim'),
                Path(FIXTURE_PATH, 'sub', '3.vim'),
                Path(FIXTURE_PATH, 'sub', '4.vim'),
            ]),
            'cwd': cwd
        }

        cmd = '-v --warning --max-violations 10 {file_paths}'.format(file_paths=FIXTURE_PATH)
        argv = cmd.split()

        # we should mock os.getcwd() because env get the cwd by os.getcwd()
        with patch('os.getcwd') as mocked_getcwd:
            mocked_getcwd.return_value = cwd
            env = build_environment(argv)

        self.maxDiff = 1000
        self.assertEqual(env, expected_env)


if __name__ == '__main__':
    unittest.main()
