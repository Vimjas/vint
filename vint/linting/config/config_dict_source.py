from vint.linting.config.config_source import ConfigSource


class ConfigDictSource(ConfigSource):
    def __init__(self, config_dict):
        self._config_dict = config_dict


    def get_config_dict(self):
        return self._config_dict
