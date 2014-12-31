from vint.ast.plugin.scope_plugin.scope_detector import ScopeDetector
from vint.ast.plugin.scope_plugin.scope_linker import ScopeLinker
from vint.ast.plugin.scope_plugin.identifier_classifier import IdentifierClassifier


REACHABILITY_FLAG = 'VINT:is_reachable'
REFERECED_FLAG = 'VINT:is_referenced'


class ReferenceReachabilityTester(object):
    """ A class for tester for reference reachabilities. """

    class TwoWayScopeReferenceAttacher(object):
        """ A class for AST processor to do attach to way reference between
        a parent scope and the child scopes.
        """

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


    def process(self, ast):
        scope_linker = ScopeLinker()
        scope_linker.process(ast)

        id_collector = IdentifierClassifier.IdentifierCollector()
        classified_id_group = id_collector.collect_identifiers(ast)
        dec_id_nodes = classified_id_group['static_declaring_identifiers']
        ref_id_nodes = classified_id_group['static_referencing_identifiers']

        self._scope_tree = scope_linker.scope_tree
        self._link_registry = scope_linker.link_registry

        # Attach a parent_scope accessor to the scope tree
        ReferenceReachabilityTester.TwoWayScopeReferenceAttacher.attach(self._scope_tree)

        # Reset REFERECED_FLAG to False
        for dec_id_node in dec_id_nodes:
            dec_id_node[REFERECED_FLAG] = False

        for ref_id_node in ref_id_nodes:
            is_reachable = self.check_reachability(ref_id_node)
            ref_id_node[REACHABILITY_FLAG] = is_reachable


    def is_global_variable(self, node):
        """ Whether the specified node is a global variable. """
        context_scope = self._link_registry.get_scope_by_referencing_identifier(node)
        if context_scope is None:
            # Looks like not variable
            return False

        return ScopeDetector.is_global_variable(node, context_scope)


    def _reset_referenced_flag(self, scope_tree):
        for child_scope in scope_tree['child_scopes']:
            for variables in child_scope['variables'].values():
                for variable in variables:
                    variable[REFERECED_FLAG] = False

            self._reset_referenced_flag(child_scope)


    def check_reachability(self, ref_id_node):
        scope = self._link_registry.get_scope_by_referencing_identifier(ref_id_node)
        var_name = ScopeDetector.normalize_variable_name(ref_id_node, scope)

        while scope is not None:
            variables = scope['variables']

            if var_name in variables:
                for variable in variables[var_name]:
                    declaring_id_node = self._link_registry.get_declarative_identifier_by_variable(variable)
                    declaring_id_node[REFERECED_FLAG] = True

                return True

            scope = scope['parent_scope']

        return False
