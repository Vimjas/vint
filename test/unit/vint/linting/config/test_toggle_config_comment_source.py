import unittest
from test.asserting.config_source import ConfigSourceAssertion
from vint.ast.node_type import NodeType
from vint.linting.config.config_toggle_comment_source import ConfigToggleCommentSource


class TestToggleConfigCommentSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        expected_config_dict = {
            'policies': {
                'Policy1': {
                    'enabled': False,
                },
                'Policy2': {
                    'enabled': True,
                },
            },
            'source_name': 'ConfigToggleCommentSource',
        }

        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1 +Policy2',
            'pos': {
                'lnum': 10,
            },
        }

        config_source = ConfigToggleCommentSource()
        config_source.update_by_node(node)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_update_by_node_by_no_switches(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint:',
            'pos': {
                'lnum': 10,
            },
        }

        expected_config_dict = {
            'policies': {},
            'source_name': 'ConfigToggleCommentSource',
        }

        config_source = ConfigToggleCommentSource()
        config_source.update_by_node(node)

        self.assertConfigDict(config_source, expected_config_dict)


    def test_update_by_node_by_single_switch(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1',
            'pos': {
                'lnum': 10,
            },
        }

        expected_config_dict = {
            'policies': {
                'Policy1': {
                    'enabled': False,
                },
            },
            'source_name': 'ConfigToggleCommentSource',
        }

        config_source = ConfigToggleCommentSource()
        config_source.update_by_node(node)

        self.assertConfigDict(config_source, expected_config_dict)


    def test_update_by_node_by_multiple_switches(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1 +Policy2',
            'pos': {
                'lnum': 10,
            },
        }

        expected_config_dict = {
            'policies': {
                'Policy1': {
                    'enabled': False,
                },
                'Policy2': {
                    'enabled': True,
                },
            },
            'source_name': 'ConfigToggleCommentSource',
        }

        config_source = ConfigToggleCommentSource()
        config_source.update_by_node(node)

        self.assertConfigDict(config_source, expected_config_dict)


if __name__ == '__main__':
    unittest.main()
