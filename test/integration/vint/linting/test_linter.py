import unittest
from pathlib import Path
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.linter import Linter

INVALID_VIM_SCRIPT = Path('test', 'fixture', 'linter', 'invalid.vim')
BROKEN_VIM_SCRIPT = Path('test', 'fixture', 'linter', 'broken.vim')


class TestLinterIntegral(unittest.TestCase):
    class StubPolicy1(AbstractPolicy):
        def __init__(self):
            super(TestLinterIntegral.StubPolicy1, self).__init__()
            self.reference = 'ref1'
            self.description = 'desc1'
            self.level = Level.WARNING


        def listen_node_types(self):
            return [NodeType.COMMENT]


        def is_valid(self, node, lint_context):
            return 'STUB_POLICY_1_INVALID' not in node['str']



    class StubPolicy2(AbstractPolicy):
        def __init__(self):
            super(TestLinterIntegral.StubPolicy2, self).__init__()
            self.reference = 'ref2'
            self.description = 'desc2'
            self.level = Level.WARNING


        def listen_node_types(self):
            return [NodeType.COMMENT]


        def is_valid(self, node, lint_context):
            return 'STUB_POLICY_2_INVALID' not in node['str']



    class StubPolicySet(object):
        def __init__(self):
            self._enabled_policies = []


        def get_enabled_policies(self):
            return self._enabled_policies


        def update_by_config(self, config_dict):
            self._enabled_policies = []

            policy_enabling_map = config_dict['policies']

            if policy_enabling_map['StubPolicy1']['enabled']:
                self._enabled_policies.append(TestLinterIntegral.StubPolicy1())

            if policy_enabling_map['StubPolicy2']['enabled']:
                self._enabled_policies.append(TestLinterIntegral.StubPolicy2())



    def test_lint(self):
        policy_set = TestLinterIntegral.StubPolicySet()

        config_dict_global = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'error-limit': 10,
            },
            'policies': {
                'StubPolicy1': {
                    'enabled': True,
                },
                'StubPolicy2': {
                    'enabled': False,
                },
            }
        }

        linter = Linter(policy_set, config_dict_global)
        got_violations = linter.lint_file(INVALID_VIM_SCRIPT)

        expected_violations = [
            {
                'name': 'StubPolicy1',
                'level': Level.WARNING,
                'description': 'desc1',
                'reference': 'ref1',
                'position': {
                    'line': 1,
                    'column': 1,
                    'path': INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'StubPolicy1',
                'level': Level.WARNING,
                'description': 'desc1',
                'reference': 'ref1',
                'position': {
                    'line': 7,
                    'column': 1,
                    'path': INVALID_VIM_SCRIPT
                },
            },
            {
                'name': 'StubPolicy2',
                'level': Level.WARNING,
                'description': 'desc2',
                'reference': 'ref2',
                'position': {
                    'line': 8,
                    'column': 1,
                    'path': INVALID_VIM_SCRIPT
                },
            },
        ]
        self.maxDiff = 1024
        self.assertEqual(got_violations, expected_violations)


    def test_lint_with_broken_file(self):
        policy_set = TestLinterIntegral.StubPolicySet()

        config_dict_global = {
            'cmdargs': {
                'verbose': True,
                'severity': Level.WARNING,
                'error-limit': 10,
            },
            'policies': {
                'StubPolicy1': {
                    'enabled': True,
                },
                'StubPolicy2': {
                    'enabled': False,
                },
            }
        }

        linter = Linter(policy_set, config_dict_global)
        got_violations = linter.lint_file(BROKEN_VIM_SCRIPT)

        expected_violations = [
            {
                'name': 'SyntaxError',
                'level': Level.ERROR,
                'description': 'unexpected token: ==',
                'reference': 'vim-jp/vim-vimlparser',
                'position': {
                    'line': 1,
                    'column': 6,
                    'path': BROKEN_VIM_SCRIPT
                },
            },
        ]

        self.maxDiff = 1000
        self.assertEqual(got_violations, expected_violations)


if __name__ == '__main__':
    unittest.main()
