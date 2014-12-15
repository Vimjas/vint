import unittest
from vint.ast.plugin.scope_plugin.scope_detector import ScopeVisibility
from vint.ast.plugin.scope_plugin.two_way_scope_reference_attacher import (
    TwoWayScopeReferenceAttacher
)


class TestTwoWayScopeReferenceAttacher(unittest.TestCase):
    def create_scope(self, scope_visibility, variables=None, child_scopes=None):
        return {
            'scope_visibility': scope_visibility,
            'variables': variables or {},
            'child_scopes': child_scopes or [],
        }


    def assertScopeTreeHasParent(self, scope_tree):
        for child_scope in scope_tree['child_scopes']:
            self.assertIs(scope_tree, child_scope['parent_scope'])
            self.assertScopeTreeHasParent(child_scope)


    def test_attach(self):
        scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            child_scopes=[
                self.create_scope(ScopeVisibility.SCRIPT_LOCAL),
            ]
        )

        attached_scope_tree = TwoWayScopeReferenceAttacher.attach(scope_tree)

        self.assertScopeTreeHasParent(attached_scope_tree)



if __name__ == '__main__':
    unittest.main()
