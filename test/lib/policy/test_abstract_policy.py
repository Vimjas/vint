import unittest
from lib.policy.abstract_policy import AbstractPolicy


class ConcretePolicy(AbstractPolicy):
    def __init__(self):
        super().__init__()
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

        env = {'path': 'path/to/file.vim'}

        expected_violation = {
            'name': 'ConcretePolicy',
            'level': 0,
            'description': 'Found something invalid',
            'reference': 'http://example.com',
            'path': 'path/to/file.vim',
            'position': pos,
        }

        policy = ConcretePolicy()
        self.assertEqual(
            policy.create_violation_report(pos, env),
            expected_violation)


if __name__ == '__main__':
    unittest.main()
