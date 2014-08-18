from lib.linting.config.config_source import ConfigSource


class ConfigCmdargsSource(ConfigSource):
    def __init__(self, env):
        super().__init__(env)
        self._config_dict = {'cmdargs': env['cmdargs']}


    def get_config_dict(self):
        return self._config_dict
