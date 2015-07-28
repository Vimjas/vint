class AbstractPolicy(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = None
        self.reference = None
        self.level = None


    def listen_node_types(self):
        """ Listening node type.
        is_valid will be called when a linter visit the listening node type.
        """
        return []


    def is_valid(self, node, lint_context):
        """ Whether the specified node is valid for the policy. """
        return True


    def create_violation_report(self, node, lint_context):
        """ Returns a violation report for the node. """
        return {
            'name': self.name,
            'level': self.level,
            'description': self.description,
            'reference': self.reference,
            'position': {
                'line': node['pos']['lnum'],
                'column': node['pos']['col'],
                'path': lint_context['path'],
            },
        }


    def get_violation_if_found(self, node, lint_context):
        """ Returns a violation if the node is invalid. """
        if self.is_valid(node, lint_context):
            return None

        return self.create_violation_report(node, lint_context)


    def get_policy_options(self, lint_context):
        policy_section = lint_context['config'].get('policies', {})
        return policy_section.get(self.name, {})
