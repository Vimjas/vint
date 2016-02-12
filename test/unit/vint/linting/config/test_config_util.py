import unittest

from vint.linting.config.config_util import get_config_value


class TestConfigUtil(unittest.TestCase):
    def test_get_config_value_when_empty(self):
        config_dict = {}

        self.assertIsNone(get_config_value(config_dict, ['a']))


    def test_get_config_value_when_nested_1_depth(self):
        config_dict = {'a': 'A'}

        self.assertIs(get_config_value(config_dict, ['a']), 'A')


    def test_get_config_value_when_nested_2_depth(self):
        config_dict = {'a': {'b': 'B'}}

        self.assertIs(get_config_value(config_dict, ['a', 'b']), 'B')


    def test_get_config_value_when_target_is_dict(self):
        config_dict = {'a': {'b': 'B'}}

        self.assertEqual(get_config_value(config_dict, ['a']), {'b': 'B'})


    def test_get_config_value_when_target_is_depth_2_unexistent_dict(self):
        config_dict = {'a': 'A'}

        self.assertEqual(get_config_value(config_dict, ['c', 'b']), None)


    def test_get_config_value_when_given_default(self):
        config_dict = {'a': 'A'}

        self.assertEqual(get_config_value(config_dict, ['c', 'b'], 'DEFAULT'), 'DEFAULT')


    def test_get_config_value_when_given_default_but_not_used(self):
        config_dict = {'a': 'A'}

        self.assertEqual(get_config_value(config_dict, ['a'], 'DEFAULT'), 'A')



if __name__ == '__main__':
    unittest.main()
