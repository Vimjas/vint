from typing import Dict
from pathlib import Path
from vint.utils.array import flat_map
from vint.asset import get_asset_path
from vint.linting.config.config_filenames import CONFIG_FILENAMES
from vint.linting.config.config_file_source import ConfigFileSource

VOID_CONFIG_PATH = get_asset_path('void_config.yaml')


class ConfigGlobalSource(ConfigFileSource):
    def get_file_path(self, env):
        global_config_paths = ConfigGlobalSource._get_filenames_candidates(env)

        for global_config_path in global_config_paths:
            if global_config_path.is_file():
                return global_config_path

        return VOID_CONFIG_PATH

    @classmethod
    def _get_filenames_candidates(cls, env):
        # type: (Dict[str, str]) -> [Path]
        global_config_dir_candidates = [
            env['xdg_config_home'],
            env['home_path'],
        ]

        return flat_map(
            lambda directory: ConfigGlobalSource._get_filenames_candidates_from_dir(directory),
            global_config_dir_candidates
        )

    @classmethod
    def _get_filenames_candidates_from_dir(cls, config_dir):
        # type: (str) -> [Path]
        return [Path(config_dir, filename) for filename in CONFIG_FILENAMES]

