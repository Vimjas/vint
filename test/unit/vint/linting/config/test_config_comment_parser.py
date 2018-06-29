import unittest
from vint.linting.config.config_comment_parser import (
    parse_config_comment,
    ConfigComment,
)



class ConfigCommentAssertion(unittest.TestCase):
    def assertConfigCommentEqual(self, a, b):
        # type: (ConfigComment, ConfigComment) -> None
        self.assertEqual(a.config_dict, b.config_dict)
        self.assertEqual(a.is_only_next_line, b.is_only_next_line)



class TestConfigCommentParser(ConfigCommentAssertion, unittest.TestCase):
    def test_parse_config_comment_empty(self):
        expected_config_comment = ConfigComment(
            config_dict={'policies': {}},
            is_only_next_line=False
        )

        config_comment = parse_config_comment(' vint:')

        self.assertConfigCommentEqual(config_comment, expected_config_comment)


    def test_parse_config_comment(self):
        expected_config_comment = ConfigComment(
            config_dict={
                'policies': {
                    'Policy1': {
                        'enabled': False,
                    },
                    'Policy2': {
                        'enabled': True,
                    },
                },
            },
            is_only_next_line=False
        )

        config_comment = parse_config_comment(' vint: -Policy1 +Policy2')

        self.assertConfigCommentEqual(config_comment, expected_config_comment)


    def test_parse_config_comment_next_line(self):
        expected_config_comment = ConfigComment(
            config_dict={
                'policies': {
                    'Policy1': {
                        'enabled': False,
                    },
                    'Policy2': {
                        'enabled': True,
                    },
                },
            },
            is_only_next_line=True
        )

        config_dict = parse_config_comment(' vint: next-line -Policy1 +Policy2')

        self.assertConfigCommentEqual(config_dict, expected_config_comment)


    def test_parse_config_comment_next_line_with_no_white_spaces(self):
        expected_config_comment = ConfigComment(
            config_dict={'policies': {}},
            is_only_next_line=True
        )

        config_dict = parse_config_comment('vint:next-line')

        self.assertConfigCommentEqual(config_dict, expected_config_comment)


    def test_parse_not_config_comment(self):
        config_comment = parse_config_comment(' not config comment')

        self.assertIsNone(config_comment)


if __name__ == '__main__':
    unittest.main()
