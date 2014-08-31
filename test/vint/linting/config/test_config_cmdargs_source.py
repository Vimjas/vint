import unittest
from test.asserting.config_source import ConfigSourceAssertion

from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.level import Level



class TestConfigFileSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        expected_config_dict = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'max-violations': 10,
            },
        }

        env = {
            'cmdargs': {
                'verbose': True,
                'style': True,
                'warning': True,
                'max-violations': 10,
            },
        }
        self.assertConfigDict(ConfigCmdargsSource,
                              expected_config_dict,
                              env)


if __name__ == '__main__':
    unittest.main()
