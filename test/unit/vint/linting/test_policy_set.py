from unittest import main, TestCase
from compat.unittest import mock
from vint.bootstrap import import_all_policies
from vint.linting.policy_set import PolicySet

PACKAGE_NAME_GETTER = 'vint.bootstrap._get_policy_package_name_for_test'
FIXTURE_PACKAGE_NAME = 'test.fixture.policy_set'


class TestPolicySet(TestCase):
    @classmethod
    # Mock policy package directory
    @mock.patch(PACKAGE_NAME_GETTER, lambda: FIXTURE_PACKAGE_NAME)
    def setUpClass(cls):
        import_all_policies()


    def test_get_enabled_policies_when_no_updated(self):
        policy_set = PolicySet()

        expected_no_policies = policy_set.get_enabled_policies()
        self.assertEqual(expected_no_policies, [],
                         'Expect all policies to be disabled')


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
