from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.plugin.scope_plugin import (
    ExplicityOfScopeVisibility,
    ScopeVisibility,
)


@register_policy
class ProhibitImplicitScopeBuiltinVariable(AbstractPolicy):
    def __init__(self):
        super(ProhibitImplicitScopeBuiltinVariable, self).__init__()
        self.reference = ':help local-variable'
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.IDENTIFIER]


    def is_valid(self, identifier, lint_context):
        """ Implicit scope builtin variables are prohibited.
        Because it will make unexpected variable name conflict between builtin
        and imlicit global/function local. For example:

            " This variable is not global variable but builtin variable.
            let count = 100
        """

        scope_plugin = lint_context['plugins']['scope']
        explicity = scope_plugin.get_explicity_of_scope_visibility(identifier)
        objective_scope_visibility = scope_plugin.get_objective_scope_visibility(identifier)

        is_valid = not (explicity is ExplicityOfScopeVisibility.IMPLICIT
                        and objective_scope_visibility is ScopeVisibility.BUILTIN)

        if not is_valid:
            self._make_description(identifier, scope_plugin)

        return is_valid


    def _make_description(self, identifier, scope_plugin):
        self.description = 'Make the scope explicit like `{good_example}` (or possibly be unexpected builtin?)'.format(
            good_example=scope_plugin.normalize_variable_name(identifier)
        )
