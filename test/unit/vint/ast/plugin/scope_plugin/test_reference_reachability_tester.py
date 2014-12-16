import unittest

from vint.ast.plugin.scope_plugin.scope_linker import ScopeVisibility, SCOPE
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.reference_reachability_tester import (
    ReferenceReachabilityTester,
    REACHABILITY_FLAG,
)
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG
)


class TestReferenceReachabilityTester(unittest.TestCase):
    def create_variable(self, id_value, is_implicit=False, is_builtin=False):
        return {
            'node': self.create_declaring_identifier(id_value),
            'is_implicit': is_implicit,
            'is_builtin': is_builtin,
        }


    def create_scope(self, scope_visibility, variables=None, child_scopes=None):
        return {
            'scope_visibility': scope_visibility,
            'variables': variables or {},
            'child_scopes': child_scopes or [],
        }


    def create_declaring_identifier(self, id_value):
        return {
            'type': NodeType.IDENTIFIER,
            'value': id_value,
            IDENTIFIER_ATTRIBUTE: {
                IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
                IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
                IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
            }
        }


    def create_referencing_identifier(self, id_value, scope):
        return {
            'type': NodeType.IDENTIFIER,
            'value': id_value,
            SCOPE: scope,
            IDENTIFIER_ATTRIBUTE: {
                IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
                IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: False,
                IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
            }
        }


    def test_process_reachable_global_var(self):
        variable_name = 'g:explicit_global_var'
        script_local_scope = self.create_scope(ScopeVisibility.SCRIPT_LOCAL)
        scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                variable_name: [self.create_variable(variable_name)],
            },
            child_scopes=[script_local_scope]
        )

        ref_id_node = self.create_referencing_identifier(
            variable_name,
            script_local_scope
        )

        tester = ReferenceReachabilityTester()
        tester.process(scope_tree, [ref_id_node])

        self.assertTrue(ref_id_node[REACHABILITY_FLAG])


    def test_process_unreachable_global_var(self):
        variable_name = 'g:explicit_global_var'
        script_local_scope = self.create_scope(ScopeVisibility.SCRIPT_LOCAL)
        scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                variable_name: [self.create_variable(variable_name)],
            },
            child_scopes=[script_local_scope]
        )

        ref_id_node = self.create_referencing_identifier(
            'g:unreachable_var',
            script_local_scope
        )

        tester = ReferenceReachabilityTester()
        tester.process(scope_tree, [ref_id_node])

        self.assertFalse(ref_id_node[REACHABILITY_FLAG])


    def test_process_reachable_global_var_from_nested_scope(self):
        variable_name = 'g:explicit_global_var'
        func_local_scope = self.create_scope(ScopeVisibility.FUNCTION_LOCAL)
        scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                variable_name: [self.create_variable(variable_name)],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    child_scopes=[func_local_scope],
                ),
            ]
        )

        ref_id_node = self.create_referencing_identifier(
            variable_name,
            func_local_scope
        )

        tester = ReferenceReachabilityTester()
        tester.process(scope_tree, [ref_id_node])

        self.assertTrue(ref_id_node[REACHABILITY_FLAG])


    def test_process_reachable_func_local_var_from_nested_scope(self):
        variable_name = 'implicit_func_local_var'

        reference_source_scope = self.create_scope(ScopeVisibility.FUNCTION_LOCAL)

        declared_scope = self.create_scope(
            ScopeVisibility.FUNCTION_LOCAL,
            variables={
                'l:' + variable_name: [
                    self.create_variable(variable_name, is_implicit=True)
                ]
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.FUNCTION_LOCAL,
                    child_scopes=[reference_source_scope]
                )
            ]
        )

        global_scope = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    child_scopes=[declared_scope],
                )
            ]
        )

        ref_id_node = self.create_referencing_identifier(
            variable_name,
            reference_source_scope,
        )

        tester = ReferenceReachabilityTester()
        tester.process(global_scope, [ref_id_node])

        self.assertTrue(ref_id_node[REACHABILITY_FLAG])


if __name__ == '__main__':
    unittest.main()
