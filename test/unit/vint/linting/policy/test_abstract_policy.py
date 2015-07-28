import unittest
from vint.linting.policy.abstract_policy import AbstractPolicy


class ConcretePolicy(AbstractPolicy):
    def __init__(self):
        super(ConcretePolicy, self).__init__()
        self.description = 'Found something invalid'
        self.reference = 'http://example.com'
        self.level = 0


class TestAbstractPolicy(unittest.TestCase):
    def test_listen_node_types(self):
        policy = AbstractPolicy()
        self.assertEqual(policy.listen_node_types(), [])

    def test_create_violation_report(self):
        pos = {
            'col': 3,
            'i': 24,
            'lnum': 3,
        }

        node = {'pos': pos}
        env = {'path': 'path/to/file.vim'}

        expected_violation = {
            'name': 'ConcretePolicy',
            'level': 0,
            'description': 'Found something invalid',
            'reference': 'http://example.com',
            'position': {
                'column': 3,
                'line': 3,
                'path': 'path/to/file.vim',
            },
        }

        policy = ConcretePolicy()
        self.assertEqual(
            policy.create_violation_report(node, env),
            expected_violation)

    def test_get_policy_options(self):
        policy = ConcretePolicy()

        expected_options = {}
        lint_context = {
            'config': {},
        }
        self.assertEqual(
            policy.get_policy_options(lint_context),
            expected_options)

        expected_options = {}
        lint_context = {
            'config': {'policies': {}},
        }
        self.assertEqual(
            policy.get_policy_options(lint_context),
            expected_options)

        expected_options = {'someoption': True}
        lint_context = {
            'config': {'policies': {'ConcretePolicy': expected_options}},
        }
        self.assertEqual(
            policy.get_policy_options(lint_context),
            expected_options)


if __name__ == '__main__':
    unittest.main()
