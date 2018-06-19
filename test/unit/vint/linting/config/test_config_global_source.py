import unittest
from test.asserting.config_source import ConfigSourceAssertion, get_fixture_path
from vint.linting.config.config_global_source import ConfigGlobalSource
from vint.linting.level import Level


class TestConfigGlobalSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        env = {
            'home_path': get_fixture_path('dummy_home'),
            'xdg_config_home': get_fixture_path('unexistent_xdg_config_home'),
        }
        expected_config_dict = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Level,
            },
            'source_name': str,
        }
        config_source = self.initialize_config_source_with_env(ConfigGlobalSource, env)
        self.assertConfigValueType(config_source, expected_config_dict)


    def test_get_config_dict_with_no_global_config(self):
        env = {
            'home_path': get_fixture_path('unexistent_home'),
            'xdg_config_home': get_fixture_path('unexistent_xdg_config_home'),
        }
        expected_config_dict = {'source_name': 'ConfigGlobalSource'}
        config_source = self.initialize_config_source_with_env(ConfigGlobalSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_get_config_dict_with_default_xdg_config_home(self):
        env = {
            'home_path': get_fixture_path('unexistent_home'),
            'xdg_config_home': get_fixture_path('xdg_config_home'),
        }
        expected_config_dict = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Level,
            },
            'source_name': str,
        }
        config_source = self.initialize_config_source_with_env(ConfigGlobalSource, env)
        self.assertConfigValueType(config_source, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
