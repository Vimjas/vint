class TwoWayScopeReferenceAttacher(object):
    @classmethod
    def attach(cls, scope_tree):
        for child_scope in scope_tree['child_scopes']:
            child_scope['parent_scope'] = scope_tree
            cls.attach(child_scope)

        return scope_tree
