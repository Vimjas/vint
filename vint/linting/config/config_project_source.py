from pathlib import Path
from vint.asset import get_asset_path
from vint.linting.config.config_file_source import ConfigFileSource

PROJECT_CONFIG_FILENAME = '.vintrc.yaml'
VOID_CONFIG_PATH = get_asset_path('void_config.yaml')


class ConfigProjectSource(ConfigFileSource):
    def get_file_path(self, env):
        proj_conf_path = VOID_CONFIG_PATH

        path_list_to_search = [Path(env['cwd'])] + list(Path(env['cwd']).parents)

        for project_path in path_list_to_search:
            proj_conf_path_tmp = project_path / PROJECT_CONFIG_FILENAME

            if proj_conf_path_tmp.is_file():
                proj_conf_path = proj_conf_path_tmp
                break

        return proj_conf_path
