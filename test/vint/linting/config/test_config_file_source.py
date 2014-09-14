import unittest
from test.asserting.config_source import ConfigSourceAssertion
from test.asserting.config_source import get_fixture_path

from vint.linting.config.config_file_source import ConfigFileSource
from vint.linting.level import Level

FIXTURE_CONFIG_FILE = get_fixture_path('fixture_config_file')


class TestConfigFileSource(ConfigSourceAssertion, unittest.TestCase):
    class ConcreteConfigFileSource(ConfigFileSource):
        def get_file_path(self, env):
            return FIXTURE_CONFIG_FILE


    def test_get_config_dict(self):
        expected_config_dict = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'error-limit': 10,
            },
            'policies': {
                'ProhibitSomethingEvil': {
                    'enabled': False,
                },
                'ProhibitSomethingDengerous': {
                    'enabled': True,
                },
            }
        }

        config_source = self.initialize_config_source_with_env(
            TestConfigFileSource.ConcreteConfigFileSource)
        self.assertConfigDict(config_source, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
