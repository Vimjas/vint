from pathlib import Path
from vint.linting.config.config_file_source import ConfigFileSource


DEFAULT_CONFIG_PATH = Path('vint', 'asset', 'default_config.yaml')


class ConfigDefaultSource(ConfigFileSource):
    def get_file_path(self, env):
        return DEFAULT_CONFIG_PATH
