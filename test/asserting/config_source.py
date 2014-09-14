import unittest
from pathlib import Path
from test.asserting.env_factory import env_factory


def get_fixture_path(filename):
    return Path('test') / 'fixture' / 'config' / filename



class ConfigSourceAssertion(unittest.TestCase):
    def initialize_config_source_with_env(self, ConfigSourceToTest, env=None):
        """ Returns a new config source instance by a common env.
        You can override the common env by the specified env argument.
        """
        return ConfigSourceToTest(env_factory(env))


    def assertConfigDict(self, config_source_to_test, expected_config_dict):
        """ Asserts that the specified ConfigSource returns a dict that is
        equivalent to the expected_config_dict.
        """
        actual_config_dict = config_source_to_test.get_config_dict()
        self.assertEqual(actual_config_dict, expected_config_dict)


    def assertConfigValueType(self, config_source_to_test,
                              expected_config_dict):
        """ Asserts that the dict that is returned by the specified ConfigSource
        has a expected type.

        You can check types by Mongo-like query:
        >>> self.assertConfigValueType(MyConfigSource, {
        >>>     'cmdargs': {'verbose': bool}
        >>> })
        """
        actual_config_dict = config_source_to_test.get_config_dict()

        self._assertConfigValueTypeInternal(actual_config_dict,
                                            expected_config_dict)


    def _assertConfigValueTypeInternal(self, actual_dict_or_value,
                                       expected_type_or_dict):
        # Support assertion by Mongo-like query
        if not isinstance(expected_type_or_dict, dict):
            expected_type = expected_type_or_dict
            actual_value = actual_dict_or_value

            self.assertIsInstance(actual_value, expected_type)
            return

        expected_dict = expected_type_or_dict
        actual_dict = actual_dict_or_value
        self.assertIsInstance(actual_dict, dict)

        for key, expected_type_or_sub_dict in expected_dict.items():
            actual_value = actual_dict[key]
            self._assertConfigValueTypeInternal(actual_value,
                                                expected_type_or_sub_dict)
