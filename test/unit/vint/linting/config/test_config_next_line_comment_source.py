import unittest
import enum
from vint.linting.linter import Linter
from vint.linting.lint_target import LintTargetFile
from vint.linting.policy_set import PolicySet
from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy

from test.asserting.config_source import ConfigSourceAssertion, get_fixture_path


class Fixtures(enum.Enum):
    SIMPLE = get_fixture_path("fixture_for_line_comment_simple.vim")
    LAMBDA_STRING_EXPR = get_fixture_path("fixture_for_line_comment_lambda_string_expr.vim")



class TestConfigNextLineCommentSource(ConfigSourceAssertion, unittest.TestCase):
    def test_simple_example(self):
        global_config_dict = {'cmdargs': {'severity': Level.ERROR}}
        policy_set = PolicySet([TestConfigNextLineCommentSource.ProhibitStringPolicy])
        linter = Linter(policy_set, global_config_dict)
        lint_target = LintTargetFile(Fixtures.SIMPLE.value)

        reported_string_node_values = [violation['description']
                                       for violation in linter.lint(lint_target)]

        self.assertEqual(reported_string_node_values, [
            "'report me because I have no line config comments'",
            "'report me because I have no line config comments, but the previous line have it'",
        ])


    def test_lambda_string_expr(self):
        global_config_dict = {'cmdargs': {'severity': Level.ERROR}}
        policy_set = PolicySet([TestConfigNextLineCommentSource.ProhibitStringPolicy])
        linter = Linter(policy_set, global_config_dict)
        lint_target = LintTargetFile(Fixtures.LAMBDA_STRING_EXPR.value)

        reported_string_node_values = [violation['description']
                                       for violation in linter.lint(lint_target)]

        self.assertEqual(reported_string_node_values, [
            "'report me because I have no line config comments'",
            "'report me because I have no line config comments, but the previous line have it'",
            # NOTE: In the current implementation, string in string will reported twice.
            "'\"report me because I have no line config comments, but the parent node have it\"'",
            '"report me because I have no line config comments, but the parent node have it"',
        ])


    class ProhibitStringPolicy(AbstractPolicy):
        def __init__(self):
            super(TestConfigNextLineCommentSource.ProhibitStringPolicy, self).__init__()
            self.description = ''
            self.reference = 'nothing'
            self.level = Level.ERROR


        def listen_node_types(self):
            return [NodeType.STRING]


        def is_valid(self, node, lint_context):
            self.description = node['value']
            return False


if __name__ == '__main__':
    unittest.main()
