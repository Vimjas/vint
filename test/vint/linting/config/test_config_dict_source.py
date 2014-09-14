import unittest

from test.asserting.config_source import ConfigSourceAssertion
from vint.linting.level import Level
from vint.linting.config.config_dict_source import ConfigDictSource



class TestConfigDictSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        config_dict = {
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

        config_source = ConfigDictSource(config_dict)

        expected_config_dict = config_dict
        self.assertConfigDict(config_source, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
