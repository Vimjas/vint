import os.path
from vint.linting.config.config_file_source import ConfigFileSource


DEFAULT_CONFIG_PATH = os.path.join('asset', 'default_config.yaml')


class ConfigDefaultSource(ConfigFileSource):
    def get_file_path(self, env):
        return DEFAULT_CONFIG_PATH
