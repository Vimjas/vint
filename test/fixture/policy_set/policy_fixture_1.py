from vint.linting.level import Level


class PolicyFixture1(object):
    def __init__(self):
        super(PolicyFixture1, self).__init__()
        self.description = 'PolicyFixture1'
        self.reference = 'PolicyFixture1'
        self.level = Level.WARNING
