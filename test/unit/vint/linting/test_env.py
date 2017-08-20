import unittest
from vint.compat.unittest import mock

from pathlib import Path
from vint.linting.env import build_environment

FIXTURE_PATH = Path('test', 'fixture', 'env')


class TestEnv(unittest.TestCase):
    def test_build_environment(self):
        cwd = Path('path', 'to', 'cwd')
        home = Path('/', 'home', 'user')
        xdg_config_home = Path('/', 'home', 'user', '.config')

        cmdargs = {
            'verbose': True,
            'warning': True,
            'max_violations': 10,
            'files': [str(FIXTURE_PATH)],
        }

        expected_env = {
            'cmdargs': {
                'files': [str(FIXTURE_PATH)],
                'verbose': True,
                'warning': True,
                'max_violations': 10,
            },
            'file_paths': set([
                Path(FIXTURE_PATH, '1.vim'),
                Path(FIXTURE_PATH, '2.vim'),
                Path(FIXTURE_PATH, 'sub', '3.vim'),
                Path(FIXTURE_PATH, 'sub', '4.vim'),
            ]),
            'home_path': home,
            'xdg_config_home': xdg_config_home,
            'cwd': cwd,
        }

        # we should mock os.getcwd() because env get the cwd by os.getcwd()
        with mock.patch('os.getcwd') as mocked_getcwd:
            mocked_getcwd.return_value = str(cwd)

            with mock.patch('os.path.expanduser') as mocked_expanduser:
                mocked_expanduser.return_value = str(home)

                with mock.patch.dict('os.environ', {'XDG_CONFIG_HOME': '/home/user/.config'}):
                    env = build_environment(cmdargs)

        self.maxDiff = 1000
        self.assertEqual(env, expected_env)


if __name__ == '__main__':
    unittest.main()
