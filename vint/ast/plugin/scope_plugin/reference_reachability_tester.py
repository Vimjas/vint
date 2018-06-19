from typing import Dict, Any, List, Union
from vint.ast.plugin.scope_plugin.scope import (
    Scope,
    VariableDeclaration,
    GlobalVariableDeclaration,
    GLOBAL_VARIABLE_DECLARATION,
    ExplicityOfScopeVisibility,
)
from vint.ast.plugin.scope_plugin.identifier_syntax import remove_optional_scope_prefix
from vint.ast.plugin.scope_plugin.scope_detector import (
    ScopeVisibilityHint,
    detect_possible_scope_visibility,
    is_builtin_variable,
)
from vint.ast.plugin.scope_plugin.scope_linker import ScopeLinker
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IdentifierClassifier,
)
from vint.ast.plugin.scope_plugin.identifier_attribute import (
    is_function_identifier,
    is_dynamic_identifier,
)


REACHABILITY_FLAG = 'VINT:is_reachable'
REFERENCED_FLAG = 'VINT:is_referenced'


class ReferenceReachabilityTesterError(Exception):
    pass


class ReferenceReachabilityTester(object):
    """ A class for tester for reference reachability. """

    class TwoWayScopeReferenceAttacher(object):
        """ A class for AST processor to do attach to way reference between
        a parent scope and the child scopes.
        """

        @classmethod
        def attach(cls, root_scope_tree):
            # type: (Scope) -> Scope
            root_scope_tree.parent = None

            return cls._attach_recursively(root_scope_tree)


        @classmethod
        def _attach_recursively(cls, scope_tree):
            # type: (Scope) -> Scope
            for child_scope in scope_tree.child_scopes:
                child_scope.parent = scope_tree
                cls._attach_recursively(child_scope)

            return scope_tree


    def __init__(self):
        self._scope_linker = ScopeLinker()  # type: ScopeLinker


    def process(self, ast):
        self._scope_linker.process(ast)

        id_collector = IdentifierClassifier.IdentifierCollector()
        classified_id_group = id_collector.collect_identifiers(ast)
        dec_id_nodes = classified_id_group.statically_declared_identifiers
        ref_id_nodes = classified_id_group.statically_referencing_identifiers

        # Attach a parent_scope accessor to the scope tree
        ReferenceReachabilityTester.TwoWayScopeReferenceAttacher.attach(self._scope_linker.scope_tree)

        # Reset REFERENCED_FLAG to False
        for dec_id_node in dec_id_nodes:
            dec_id_node[REFERENCED_FLAG] = False

        for ref_id_node in ref_id_nodes:
            is_reachable = self.check_reachability(ref_id_node)
            ref_id_node[REACHABILITY_FLAG] = is_reachable


    def get_objective_scope_visibility(self, decl_or_ref_id_node): # type: (Dict[str, Any]) -> ScopeVisibilityHint
        """ Returns a objective scope visibility by a declarative identifier node or a reference identifier node. """
        context_scope = self._scope_linker.link_registry.get_context_scope_by_identifier(decl_or_ref_id_node)
        possible_visibility_hint = detect_possible_scope_visibility(decl_or_ref_id_node, context_scope)
        possible_explicity = possible_visibility_hint.explicity

        # Return the visibility soon if the node already have a determined visibility.
        if possible_explicity is not ExplicityOfScopeVisibility.IMPLICIT_OR_LAMBDA:
            determined_visibility_hint = possible_visibility_hint
            return determined_visibility_hint

        # The node have IMPLICIT_OR_LAMBDA can be only reference identifier nodes.
        # SEE: detect_possible_scope_visibility
        ref_id_node = decl_or_ref_id_node

        # It is constrained implicit if it is a lambda argument.
        if self._is_reference_to_lambda_argument(ref_id_node):
            return ScopeVisibilityHint(
                scope_visibility=possible_visibility_hint.scope_visibility,
                explicity=ExplicityOfScopeVisibility.IMPLICIT_BUT_CONSTRAINED,
            )

        # Otherwise it is implicit.
        return ScopeVisibilityHint(
            scope_visibility=possible_visibility_hint.scope_visibility,
            explicity=ExplicityOfScopeVisibility.IMPLICIT
        )



    def _reset_referenced_flag(self, scope_tree): # type: (Scope) -> None
        for child_scope in scope_tree.child_scopes:
            for functions in child_scope.functions.values():
                for func in functions:
                    decl_id_node = self._scope_linker.link_registry.get_declarative_identifier_by_variable(func)
                    decl_id_node[REFERENCED_FLAG] = False

            for variables in child_scope.variables.values():
                for variable in variables:
                    decl_id_node = self._scope_linker.link_registry.get_declarative_identifier_by_variable(variable)
                    decl_id_node[REFERENCED_FLAG] = False

            self._reset_referenced_flag(child_scope)


    def get_referenced_variable_declarations(self, ref_id_node):
        # type: (Dict[str, Any]) -> Union[List[VariableDeclaration], GlobalVariableDeclaration]

        scope = self._scope_linker.link_registry.get_context_scope_by_identifier(ref_id_node)
        var_name = remove_optional_scope_prefix(ref_id_node['value'])
        is_func_id = is_function_identifier(ref_id_node)

        while scope is not None:
            if is_func_id:
                functions_list = scope.functions
                if var_name in functions_list:
                    # The function is found in the symbol table for functions.
                    funcs = functions_list[var_name]

                    for func in funcs:
                        declaring_id_node = self._scope_linker.link_registry \
                            .get_declarative_identifier_by_variable(func)
                        declaring_id_node[REFERENCED_FLAG] = True

                    return funcs
                else:
                    # We can access the function via a variable function
                    # reference if the function not found from the symbol table
                    # for functions. So we should check the symbol table for
                    # variables to search the function reference.
                    pass

            variables_list = scope.variables
            if var_name in variables_list:
                # The variable or function reference found in the symbol table
                # for variables.
                variables = variables_list[var_name]

                for variable in variables:
                    declaring_id_node = self._scope_linker.link_registry \
                        .get_declarative_identifier_by_variable(variable)
                    declaring_id_node[REFERENCED_FLAG] = True

                return variables

            scope = scope.parent

        # If it is builtin, it will be used by Vim.
        if is_builtin_variable(ref_id_node):
            return GLOBAL_VARIABLE_DECLARATION

        return []


    def check_reachability(self, ref_id_node): # type: (Dict[str, Any]) -> bool
        # NOTE: We can only assume dynamic identifiers can reach.
        if is_dynamic_identifier(ref_id_node):
            return True

        declarative_variables_or_global = self.get_referenced_variable_declarations(ref_id_node)

        if isinstance(declarative_variables_or_global, GlobalVariableDeclaration):
            # NOTE: It is a global like variable, so we can only assume it can reach.
            return True

        # NOTE: It is reachable if at least one declarative identifier can reach to found.
        return len(declarative_variables_or_global) > 0


    def _is_reference_to_lambda_argument(self, ref_id_node): # type: (Dict[str, Any]) -> bool
        # NOTE: We can only assume dynamic identifiers can reach.
        if is_dynamic_identifier(ref_id_node):
            return True

        declarative_variables_or_global = self.get_referenced_variable_declarations(ref_id_node)

        if isinstance(declarative_variables_or_global, GlobalVariableDeclaration):
            return False

        declarative_variables = declarative_variables_or_global

        for declarative_variable in declarative_variables:
            if declarative_variable.is_explicit_lambda_argument:
                return True

        return False


def is_reference_identifier(node):
    return REACHABILITY_FLAG in node


def is_reachable_reference_identifier(node):
    return node.get(REACHABILITY_FLAG, False)


def is_declarative_identifier(node):
    return REFERENCED_FLAG in node


def is_referenced_declarative_identifier(node):
    return node.get(REFERENCED_FLAG, False)
