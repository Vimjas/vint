from vint.ast.plugin.scope_plugin.scope_detector import ScopeDetector
from vint.ast.plugin.scope_plugin.scope_linker import SCOPE


REACHABILITY_FLAG = 'VINT:is_reachable'
REFERECED_FLAG = 'VINT:is_referenced'


class ReferenceReachabilityTester(object):
    class TwoWayScopeReferenceAttacher(object):
        @classmethod
        def attach(cls, root_scope_tree):
            root_scope_tree['parent_scope'] = None

            return cls._attach_recursively(root_scope_tree)


        @classmethod
        def _attach_recursively(cls, scope_tree):
            for child_scope in scope_tree['child_scopes']:
                child_scope['parent_scope'] = scope_tree
                cls._attach_recursively(child_scope)

            return scope_tree


    def process(self, scope_tree, ref_id_nodes):
        ReferenceReachabilityTester.TwoWayScopeReferenceAttacher.attach(scope_tree)

        for ref_id_node in ref_id_nodes:
            is_reachable = self.check_reachability(ref_id_node)
            ref_id_node[REACHABILITY_FLAG] = is_reachable


    def _reset_referenced_flag(self, scope_tree):
        for child_scope in scope_tree['child_scopes']:
            for variables in child_scope['variables'].values():
                for variable in variables:
                    variable[REFERECED_FLAG] = False

            self._reset_referenced_flag(child_scope)



    def check_reachability(self, ref_id_node):
        scope = ref_id_node[SCOPE]
        var_name = ScopeDetector.normalize_variable_name(ref_id_node, scope)

        while scope is not None:
            variables = scope['variables']

            if var_name in variables:
                for variable in variables[var_name]:
                    variable[var_name][REFERECED_FLAG] = True

                return True

            scope = scope['parent_scope']

        return False
