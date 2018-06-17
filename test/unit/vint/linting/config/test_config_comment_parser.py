import unittest
from test.asserting.config_source import ConfigSourceAssertion
from vint.linting.config.config_comment_parser import (
    parse_config_comment,
)


class TestConfigCommentParser(ConfigSourceAssertion, unittest.TestCase):
    def test_parse_config_comment_empty(self):
        expected_config_dict = {}

        config_dict = parse_config_comment(' vint:')

        self.assertEqual(config_dict, expected_config_dict)


    def test_parse_config_comment(self):
        expected_config_dict = {
            'Policy1': {
                'enabled': False,
            },
            'Policy2': {
                'enabled': True,
            },
        }

        config_dict = parse_config_comment(' vint: -Policy1 +Policy2')

        self.assertEqual(config_dict, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
