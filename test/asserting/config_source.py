import unittest
from pathlib import Path


def get_fixture_path(filename):
    return Path('test') / 'fixture' / 'config' / filename


def env_factory(prior_env=None):
    preset_env = {
        'cwd': Path('path') / 'to' / 'project',
        'cmd_args': {
            'verbose': True,
        },
        'home_path': Path('/') / 'home' / 'vint',
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
    def _build_config_source(self, ConfigSourceToTest, env=None):
        """ Returns a new config source instance by a common env.
        You can override the common env by the specified env argument.
        """
        return ConfigSourceToTest(env_factory(env))


    def assertConfigDict(self, ConfigSourceToTest, expected_config_dict, env=None):
        """ Asserts that the specified ConfigSource returns a dict that is
        equivalent to the expected_config_dict.
        """
        config_source = self._build_config_source(ConfigSourceToTest, env)

        actual_config_dict = config_source.get_config_dict()
        self.assertEqual(actual_config_dict, expected_config_dict)


    def assertConfigValueType(self, ConfigSourceToTest, expected_config_dict, env=None):
        """ Asserts that the dict that is returned by the specified ConfigSource
        has a expected type.

        You can check types by Mongo-like query:
        >>> self.assertConfigValueType(MyConfigSource, {
        >>>     'cmdargs': {'verbose': bool}
        >>> })
        """
        config_source = self._build_config_source(ConfigSourceToTest, env)
        actual_config_dict = config_source.get_config_dict()

        self._assertConfigValueTypeInternal(actual_config_dict,
                                            expected_config_dict,
                                            env)


    def _assertConfigValueTypeInternal(self, actual_dict_or_value,
                                       expected_type_or_dict, env=None):
        # Support assertion by Mongo-like query
        if not isinstance(expected_type_or_dict, dict):
            expected_type = expected_type_or_dict
            actual_value = actual_dict_or_value

            self.assertIsInstance(actual_value, expected_type)
            return

        expected_dict = expected_type_or_dict
        actual_dict = actual_dict_or_value
        self.assertIsInstance(actual_dict, dict)

        for key, expected_type_or_sub_dict in expected_dict.items():
            actual_value = actual_dict[key]
            self._assertConfigValueTypeInternal(actual_value,
                                                expected_type_or_sub_dict,
                                                env)
