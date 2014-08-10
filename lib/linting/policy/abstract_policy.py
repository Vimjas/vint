class AbstractPolicy(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = None
        self.reference = None
        self.level = None


    def listen_node_types(self):
        return []


    def is_valid(self, node, env):
        return True


    def create_violation_report(self, node, env):
        return {
            'name': self.name,
            'level': self.level,
            'description': self.description,
            'reference': self.reference,
            'position': {
                'line': node['pos']['lnum'],
                'column': node['pos']['col'],
                'path': env['path'],
            },
        }


    def get_violation_if_found(self, node, env):
        if self.is_valid(node, env):
            return None

        return self.create_violation_report(node, env)
