import unittest
from pathlib import Path
from enum import Enum
from test.asserting.config_source import ConfigSourceAssertion, get_fixture_path
from vint.linting.config.config_project_source import ConfigProjectSource


class TestConfigProjectSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        env = {
            'cwd': get_fixture_path('project_with_long_extname')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }

        config_source = self.initialize_config_source_with_env(ConfigProjectSource, env)
        self.assertConfigValueType(config_source, expected_type)


    def test_get_config_dict_on_sub_directory(self):
        env = {
            'cwd': get_fixture_path(Path('project_with_long_extname') / 'sub' / 'subsub')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }

        config_source = self.initialize_config_source_with_env(ConfigProjectSource, env)
        self.assertConfigValueType(config_source, expected_type)


    def test_get_config_dict_for_short_extname(self):
        env = {
            'cwd': get_fixture_path('project_with_short_extname')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }

        config_source = self.initialize_config_source_with_env(ConfigProjectSource, env)
        self.assertConfigValueType(config_source, expected_type)


    def test_get_config_dict_for_no_extname(self):
        env = {
            'cwd': get_fixture_path('project_with_no_extname')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }

        config_source = self.initialize_config_source_with_env(ConfigProjectSource, env)
        self.assertConfigValueType(config_source, expected_type)


    def test_get_config_dict_with_no_global_config(self):
        env = {
            'cwd': get_fixture_path('unexistent_project')
        }

        expected_config_dict = {}

        config_source = self.initialize_config_source_with_env(ConfigProjectSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
