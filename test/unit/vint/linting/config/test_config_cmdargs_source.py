import unittest
from test.asserting.config_source import ConfigSourceAssertion

from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.level import Level


class TestConfigFileSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        env = {
            'cmdargs': {
                'verbose': True,
                'style': True,
                'warning': True,
                'max-violations': 10,
            },
        }

        expected_config_dict = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'max-violations': 10,
            },
        }

        config_source = self.initialize_config_source_with_env(ConfigCmdargsSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_get_config_dict_with_no_severity(self):
        env = {'cmdargs': {}}

        expected_config_dict = {'cmdargs': {}}

        config_source = self.initialize_config_source_with_env(ConfigCmdargsSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_get_config_dict_with_severity_style_problem(self):
        env = {
            'cmdargs': {
                'style_problem': True,
            },
        }

        expected_config_dict = {
            'cmdargs': {
                'severity': Level.STYLE_PROBLEM,
            },
        }

        config_source = self.initialize_config_source_with_env(ConfigCmdargsSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_get_config_dict_with_severity_warning(self):
        env = {
            'cmdargs': {
                'warning': True,
            },
        }

        expected_config_dict = {
            'cmdargs': {
                'severity': Level.WARNING,
            },
        }

        config_source = self.initialize_config_source_with_env(ConfigCmdargsSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_get_config_dict_with_severity_error(self):
        env = {
            'cmdargs': {
                'error': True,
            },
        }

        expected_config_dict = {
            'cmdargs': {
                'severity': Level.ERROR,
            },
        }

        config_source = self.initialize_config_source_with_env(ConfigCmdargsSource, env)
        self.assertConfigDict(config_source, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
