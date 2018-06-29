from typing import Dict, Any
from vint.linting.config.config_source import ConfigSource


class ConfigDictSource(ConfigSource):
    def __init__(self, config_dict):
        # type: (Dict[str, Any]) -> None
        self._config_dict = config_dict.copy()

        # For debugging.
        self._config_dict['source_name'] = self.__class__.__name__


    def get_config_dict(self):
        # type: () -> Dict[str, Any]
        return self._config_dict
