class AbstractPolicy(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = None
        self.reference = None
        self.level = None
        self.violations = []


    def listen_node_types(self):
        return []


    def visit_node(self):
        pass


    def create_violation_report(self, pos, env):
        return {
            'name': self.name,
            'level': self.level,
            'description': self.description,
            'reference': self.reference,
            'path': env['path'],
            'position': pos,
        }


    def is_valid(self, node, root):
        return True
