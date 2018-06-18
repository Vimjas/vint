from typing import Dict, Any
from vint.linting.config.config_source import ConfigSource


class ConfigAbstractDynamicSource(ConfigSource):
    """ A abstract class for ConfigSource that dynamically changed when linting. """
    def __init__(self):
        pass


    def get_config_dict(self):
        # type: () -> Dict[str, Any]
        raise NotImplementedError()


    def update_by_node(self, node):
        # type: (Dict[str, Any]) -> None
        raise NotImplementedError()
