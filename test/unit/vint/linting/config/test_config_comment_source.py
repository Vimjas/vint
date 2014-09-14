import unittest
from test.asserting.config_source import ConfigSourceAssertion
from vint.ast.node_type import NodeType
from vint.linting.config.config_comment_source import ConfigCommentSource


class TestConfigCommentSource(ConfigSourceAssertion, unittest.TestCase):
    def test_get_config_dict(self):
        expected_config_dict = {
            'policies': {
                'Policy1': {
                    'enabled': False,
                },
                'Policy2': {
                    'enabled': True,
                },
            }
        }

        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1 +Policy2',
        }

        config_source = ConfigCommentSource()
        config_source.update_by_node(node)
        self.assertConfigDict(config_source, expected_config_dict)


    def test_update_by_node_by_no_switches(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint:',
        }

        expected_config_dict = {
            'policies': {}
        }

        config_source = ConfigCommentSource()
        config_source.update_by_node(node)

        self.assertConfigDict(config_source, expected_config_dict)


    def test_update_by_node_by_single_switch(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1',
        }

        expected_config_dict = {
            'policies': {
                'Policy1': {
                    'enabled': False,
                },
            }
        }

        config_source = ConfigCommentSource()
        config_source.update_by_node(node)

        self.assertConfigDict(config_source, expected_config_dict)


    def test_update_by_node_by_multiple_switches(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1 +Policy2',
        }

        expected_config_dict = {
            'policies': {
                'Policy1': {
                    'enabled': False,
                },
                'Policy2': {
                    'enabled': True,
                },
            }
        }

        config_source = ConfigCommentSource()
        config_source.update_by_node(node)

        self.assertConfigDict(config_source, expected_config_dict)


    def test_is_requesting_update_when_config_comment_arrived(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' vint: -Policy1 +Policy2',
        }

        config_source = ConfigCommentSource()
        is_requesting_update = config_source.is_requesting_update(node)

        self.assertTrue(is_requesting_update, 'Expected true was returned')


    def test_is_requesting_update_when_just_comment_arrived(self):
        node = {
            'type': NodeType.COMMENT,
            'str': ' Lorem ipsum',
        }

        config_source = ConfigCommentSource()
        is_requesting_update = config_source.is_requesting_update(node)

        self.assertFalse(is_requesting_update, 'Expected false was returned')


    def test_is_requesting_update_when_other_node_arrived(self):
        node = {
            'type': NodeType.EXCALL,
        }

        config_source = ConfigCommentSource()
        is_requesting_update = config_source.is_requesting_update(node)

        self.assertFalse(is_requesting_update, 'Expected false was returned')


if __name__ == '__main__':
    unittest.main()
