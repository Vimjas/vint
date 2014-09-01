import unittest
from pathlib import Path
from enum import Enum
from test.asserting.config_source import ConfigSourceAssertion, get_fixture_path
from vint.linting.config.config_project_source import ConfigProjectSource


class TestConfigProjectSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        env = {
            'cwd': get_fixture_path('project')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }
        self.assertConfigValueType(ConfigProjectSource, expected_type, env)


    def test_get_config_dict_on_sub_directory(self):
        env = {
            'cwd': get_fixture_path(Path('project') / 'sub' / 'subsub')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }
        self.assertConfigValueType(ConfigProjectSource, expected_type, env)


    def test_get_config_dict_with_no_global_config(self):
        env = {
            'cwd': get_fixture_path('unexistent_project')
        }

        expected_config_dict = {}
        self.assertConfigDict(ConfigProjectSource, expected_config_dict, env)


if __name__ == '__main__':
    unittest.main()
