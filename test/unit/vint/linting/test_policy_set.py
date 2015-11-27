from unittest import main, TestCase
from vint.compat.unittest import mock

from pprint import pprint
from vint.linting.policy_set import PolicySet
from vint.linting.level import Level

from test.fixture.policy_set.policy_fixture_1 import PolicyFixture1
from test.fixture.policy_set.policy_fixture_2 import PolicyFixture2


@mock.patch('vint.linting.policy_registry.get_policy_class_map', lambda: {
    'PolicyFixture1': PolicyFixture1,
    'PolicyFixture2': PolicyFixture2,
})
class TestPolicySet(TestCase):
    def test_get_enabled_policies_when_no_updated(self):
        policy_set = PolicySet()

        expected_no_policies = policy_set.get_enabled_policies()
        self.assertEqual(expected_no_policies, [],
                         'Expect all policies to be disabled')


    def assertEnabledPolicies(self, expected_enabled_policy_classes, actual_enabled_policies):
        actual_enabled_policy_classes = {enabled_policy_class: False
                                         for enabled_policy_class
                                         in expected_enabled_policy_classes}

        for actual_enabled_policy in actual_enabled_policies:
            actual_enabled_policy_classes[actual_enabled_policy.__class__] = True

        pprint(actual_enabled_policy_classes)
        assert all(actual_enabled_policy_classes.values())


    def test_get_enabled_policies_with_a_disabled_option(self):
        config_dict = {
            'cmdargs': {
                'severity': Level.WARNING,
            },
            'policies': {
                'PolicyFixture1': {
                    'enabled': True,
                },
                'PolicyFixture2': {
                    'enabled': False,
                },
            }
        }

        policy_set = PolicySet()
        policy_set.update_by_config(config_dict)

        actual_enabled_policies = policy_set.get_enabled_policies()

        expected_enabled_policy_classes = [
            PolicyFixture1,
        ]

        self.assertEnabledPolicies(expected_enabled_policy_classes, actual_enabled_policies)


    def test_get_enabled_policies_with_severity_warning(self):
        config_dict = {
            'cmdargs': {
                'severity': Level.WARNING,
            },
            'policies': {}
        }

        policy_set = PolicySet()
        policy_set.update_by_config(config_dict)

        actual_enabled_policies = policy_set.get_enabled_policies()

        expected_enabled_policy_classes = [
            PolicyFixture1,
        ]

        self.assertEnabledPolicies(expected_enabled_policy_classes, actual_enabled_policies)


    def test_get_enabled_policies_with_severity_style_problem(self):
        config_dict = {
            'cmdargs': {
                'severity': Level.STYLE_PROBLEM,
            },
            'policies': {}
        }

        policy_set = PolicySet()
        policy_set.update_by_config(config_dict)

        actual_enabled_policies = policy_set.get_enabled_policies()

        expected_enabled_policy_classes = [
            PolicyFixture1,
            PolicyFixture2,
        ]

        self.assertEnabledPolicies(expected_enabled_policy_classes, actual_enabled_policies)


if __name__ == '__main__':
    main()
