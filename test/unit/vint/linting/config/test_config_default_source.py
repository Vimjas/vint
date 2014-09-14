import unittest
from enum import Enum
from test.asserting.config_source import ConfigSourceAssertion
from vint.linting.config.config_default_source import ConfigDefaultSource


class TestConfigDefaultSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        expected_type = {
            'cmdargs': {
                'verbose': bool,
                'error-limit': int,
                'severity': Enum,
            }
        }

        config_source = self.initialize_config_source_with_env(ConfigDefaultSource)
        self.assertConfigValueType(config_source, expected_type)

if __name__ == '__main__':
    unittest.main()
