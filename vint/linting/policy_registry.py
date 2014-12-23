# For dynamic policy module import
_policy_class_map = {}


def register_policy(PolicyClass):
    policy_name = PolicyClass.__name__
    _policy_class_map[policy_name] = PolicyClass
    return PolicyClass


def get_policy_class_map():
    return _policy_class_map
