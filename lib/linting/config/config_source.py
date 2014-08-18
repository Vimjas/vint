class ConfigSource(object):
    def __init__(self, env):
        pass


    def get_config_dict(self):
        raise NotImplementedError()


    def convert_to_python_var_name(self, var_name):
        """ Convert command-line arg-style variable name to python-style.

        This method is designed to making config/command-line arg understandability for user. """
        return var_name.replace('-', '_')
