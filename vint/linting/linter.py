from vint.ast.parsing import Parser
from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType


class Linter(object):
    def __init__(self, policies):
        self.parser = Parser()
        self.policies = policies
        self.violations = []

        self._listeners_map = self.build_listeners_map(policies)


    def lint(self, path):
        root_ast = self.parser.parse_file(path)

        # Given root AST to make policy flexibility
        env = {'path': path, 'root': root_ast}
        traverse(lambda node: self.visit_node(node, env), root_ast)

        return self.violations


    def visit_node(self, node, env):
        node_type = NodeType(node['type'])

        if node_type not in self._listeners_map:
            return

        listening_policies = self._listeners_map[node_type]

        for listening_policy in listening_policies:
            violation = listening_policy.get_violation_if_found(node, env)

            if violation is not None:
                self.violations.append(violation)


    def build_listeners_map(self, policies):
        lisnters_map = {}

        for policy in self.policies:
            listened_node_types = policy.listen_node_types()

            for listened_node_type in listened_node_types:
                if listened_node_type not in lisnters_map:
                    lisnters_map[listened_node_type] = [policy]
                else:
                    lisnters_map[listened_node_type].append(policy)

        return lisnters_map
