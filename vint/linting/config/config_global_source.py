import os.path
from vint.linting.config.config_file_source import ConfigFileSource

GLOBAL_CONFIG_FILENAME = '.vintrc.yaml'
VOID_CONFIG_PATH = os.path.join('asset', 'void_config.yaml')


class ConfigGlobalSource(ConfigFileSource):
    def get_file_path(self, env):
        global_config_path = os.path.join(env['home_path'],
                                          GLOBAL_CONFIG_FILENAME)

        print(global_config_path)
        print(os.path.isfile(global_config_path))

        if os.path.isfile(global_config_path):
            return global_config_path
        else:
            return VOID_CONFIG_PATH
