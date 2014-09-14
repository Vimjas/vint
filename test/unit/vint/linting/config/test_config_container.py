import unittest
from test.asserting.config_source import ConfigSourceAssertion

from vint.linting.config.config_source import ConfigSource
from vint.linting.config.config_container import ConfigContainer
from vint.linting.level import Level


class TestConfigContainer(ConfigSourceAssertion, unittest.TestCase):
    class StubConfigSource(ConfigSource):
        def __init__(self, config_dict):
            self.return_value = config_dict


        def get_config_dict(self):
            return self.return_value


    def test_get_config_dict(self):
        config_dicts = (
            {  # Default source
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
            },
            {  # Somthing to overwrite
                'cmdargs': {
                    'error-limit': 20,
                },
                'policies': {
                    'ProhibitSomethingEvil': {
                        'enabled': True,
                    },
                }
            },
            {},  # Somthing to overwrite but no affect
        )

        config_sources = [TestConfigContainer.StubConfigSource(config_dict)
                          for config_dict in config_dicts]

        config_container = ConfigContainer(*config_sources)

        expected_config_dict = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'error-limit': 20,
            },
            'policies': {
                'ProhibitSomethingEvil': {
                    'enabled': True,
                },
                'ProhibitSomethingDengerous': {
                    'enabled': True,
                },
            }
        }

        self.assertConfigDict(config_container, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
