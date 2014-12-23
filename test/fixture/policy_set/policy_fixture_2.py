from vint.linting.level import Level


class PolicyFixture2(object):
    def __init__(self):
        super(PolicyFixture2, self).__init__()
        self.description = 'PolicyFixture2'
        self.reference = 'PolicyFixture2'
        self.level = Level.STYLE_PROBLEM
