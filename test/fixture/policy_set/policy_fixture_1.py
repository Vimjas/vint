from vint.linting.policy_loader import register_policy


@register_policy
class PolicyFixture1(object):
    def __init__(self):
        pass
