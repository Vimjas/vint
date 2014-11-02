from unittest import main, skip, TestCase
from compat.unittest import mock
from vint.linting.policy_loader import get_policy_class_map
from vint.linting.policy_set import PolicySet, import_all_policies

PACKAGE_NAME_GETTER = 'vint.linting.policy_set._get_policy_package_name_for_test'
FIXTURE_PACKAGE_NAME = 'test.fixture.policy_set'


class TestPolicySet(TestCase):
    @skip('This test is very fragile because it depends to run sequence')
    @mock.patch(PACKAGE_NAME_GETTER, lambda: FIXTURE_PACKAGE_NAME)
    def test_import_all_policies(self):
        """ Expect policy classes to be imported. """
        policy_class_map_before_importing = get_policy_class_map()
        self.assertNotIn('PolicyFixture1', policy_class_map_before_importing)
        self.assertNotIn('PolicyFixture2', policy_class_map_before_importing)

        import_all_policies()

        policy_class_map_after_imported = get_policy_class_map()
        self.assertIn('PolicyFixture1', policy_class_map_after_imported)
        self.assertIn('PolicyFixture2', policy_class_map_after_imported)


    # Mock policy package directory
    @mock.patch(PACKAGE_NAME_GETTER, lambda: FIXTURE_PACKAGE_NAME)
    def test_get_enabled_policies_when_no_updated(self):
        policy_set = PolicySet()

        expected_no_policies = policy_set.get_enabled_policies()
        self.assertEqual(expected_no_policies, [],
                         'Expect all policies to be disabled')


    # Mock policy package directory
    @mock.patch(PACKAGE_NAME_GETTER, lambda: FIXTURE_PACKAGE_NAME)
    def test_get_enabled_policies(self):
        policy_enabling_map_to_enable_policy1 = {
            'PolicyFixture1': {
                'enabled': True,
            },
            'PolicyFixture2': {
                'enabled': False,
            },
        }

        policy_set = PolicySet()
        policy_set.update_by_config(policy_enabling_map_to_enable_policy1)

        expected_policy1_to_be_enabled = policy_set.get_enabled_policies()
        self.assertEqual(len(expected_policy1_to_be_enabled), 1,
                         'Expect number of enabled policies to equal 1')

        from test.fixture.policy_set.policy_fixture_1 import PolicyFixture1
        self.assertIsInstance(expected_policy1_to_be_enabled[0], PolicyFixture1,
                              'Expect policy1 to be enabled')


if __name__ == '__main__':
    main()
