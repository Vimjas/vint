import unittest
from enum import Enum
from test.asserting.config_source import ConfigSourceAssertion, get_fixture_path
from vint.linting.config.config_global_source import ConfigGlobalSource


class TestConfigGlobalSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        env = {
            'home_path': get_fixture_path('dummy_home')
        }

        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }
        self.assertConfigValueType(ConfigGlobalSource, expected_type, env)


    def test_get_config_dict_with_no_global_config(self):
        env = {
            'home_path': get_fixture_path('unexistent_home')
        }

        expected_config_dict = {}
        self.assertConfigDict(ConfigGlobalSource, expected_config_dict, env)


if __name__ == '__main__':
    unittest.main()
