from vint.ast.plugin.scope_plugin.scope_detector import (
    detect_scope_visibility,
    normalize_variable_name,
    is_builtin_variable,
)
from vint.ast.plugin.scope_plugin.scope_linker import ScopeLinker
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IdentifierClassifier,
    is_function_identifier,
)


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


    def get_objective_scope_visibility(self, node):
        """ Returns a objective scope visibility. """
        context_scope = self._link_registry.get_scope_by_referencing_identifier(node)
        return detect_scope_visibility(node, context_scope)['scope_visibility']


    def _reset_referenced_flag(self, scope_tree):
        for child_scope in scope_tree['child_scopes']:
            for functions in child_scope['functions'].values():
                for function in functions:
                    function[REFERECED_FLAG] = False

            for variables in child_scope['variables'].values():
                for variable in variables:
                    variable[REFERECED_FLAG] = False

            self._reset_referenced_flag(child_scope)


    def check_reachability(self, ref_id_node):
        scope = self._link_registry.get_context_scope_by_identifier(ref_id_node)
        var_name = normalize_variable_name(ref_id_node, scope)
        is_func_id = is_function_identifier(ref_id_node)

        while scope is not None:
            if is_func_id:
                functions_list = scope['functions']
                if var_name in functions_list:
                    # The function is found in the symbol table for functions.
                    for variable in functions_list[var_name]:
                        declaring_id_node = self._link_registry\
                            .get_declarative_identifier_by_variable(variable)
                        declaring_id_node[REFERECED_FLAG] = True

                    return True
                else:
                    # We can access the function via a variable function
                    # reference if the function not found from the symbol table
                    # for functions. So we should check the symbol table for
                    # variables to search the function reference.
                    pass

            variables_list = scope['variables']
            if var_name in variables_list:
                # The variable or function reference found in the symbol table
                # for variables.
                for variable in variables_list[var_name]:
                    declaring_id_node = self._link_registry\
                        .get_declarative_identifier_by_variable(variable)
                    declaring_id_node[REFERECED_FLAG] = True

                return True

            scope = scope['parent_scope']

        # If it is builtin, it will be used by Vim.
        return is_builtin_variable(ref_id_node)


def is_reference_identifier(node):
    return REACHABILITY_FLAG in node


def is_reachable_reference_identifier(node):
    return node.get(REACHABILITY_FLAG, False)


def is_declarative_identifier(node):
    return REFERECED_FLAG in node


def is_referenced_declarative_identifier(node):
    return node.get(REFERECED_FLAG, False)
