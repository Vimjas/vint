class ConfigSource(object):
    class ConfigError(Exception):
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return self.msg


    def __init__(self, env):
        pass


    def get_config_dict(self):
        raise NotImplementedError()
