import unittest
import os.path


def get_fixture_path(filename):
    return os.path.join('test', 'fixture', 'config', filename)


def env_factory(prior_env):
    preset_env = {
        'cwd': 'path/to/project',
        'cmd_args': {
            'verbose': True,
        },
        'file_paths': [
            '1.vim',
            '2.vim',
            '3.vim',
        ],
    }

    if prior_env is None:
        return preset_env

    preset_env.update(prior_env)
    return preset_env



class ConfigSourceAssertion(unittest.TestCase):
    def assertConfigDict(self, ConfigSourceToTest, env, expected_config_dict):
        config_source = ConfigSourceToTest(env_factory(env))

        actual_config_dict = config_source.get_config_dict()
        self.assertEqual(actual_config_dict, expected_config_dict)
