from vint.asset import get_asset_path
from vint.linting.config.config_file_source import ConfigFileSource


DEFAULT_CONFIG_PATH = get_asset_path('default_config.yaml')


class ConfigDefaultSource(ConfigFileSource):
    def get_file_path(self, env):
        return DEFAULT_CONFIG_PATH
