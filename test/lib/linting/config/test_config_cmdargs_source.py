import unittest
from test.asserting.config_source import ConfigSourceAssertion

from lib.linting.config.config_cmdargs_source import ConfigCmdargsSource
from lib.linting.level import Level



class TestConfigFileSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        expected_config_dict = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'error-limit': 10,
            },
        }

        env = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'error-limit': 10,
            },
        }
        self.assertConfigDict(ConfigCmdargsSource,
                              env,
                              expected_config_dict)


if __name__ == '__main__':
    unittest.main()
