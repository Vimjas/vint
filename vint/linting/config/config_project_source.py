from pathlib import Path
from vint.asset import get_asset_path
from vint.linting.config.config_file_source import ConfigFileSource

PROJECT_CONFIG_FILENAMES = [
    '.vintrc.yaml',
    '.vintrc.yml',
    '.vintrc',
]


class ConfigProjectSource(ConfigFileSource):
    def get_file_path(self, env):
        cwd = Path(env['cwd'])
        path_list_to_search = [cwd] + list(cwd.parents)

        for project_path in path_list_to_search:
            for basename in PROJECT_CONFIG_FILENAMES:
                proj_conf_path_tmp = project_path / basename

                if proj_conf_path_tmp.is_file():
                    return proj_conf_path_tmp

        return get_asset_path('void_config.yaml')
