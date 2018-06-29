from typing import Dict, Any
from pathlib import Path
import yaml
import logging
from vint.linting.config.config_source import ConfigSource
from vint.linting.level import Level



class ConfigFileSource(ConfigSource):
    def __init__(self, env):
        # type: (Dict[str, Any]) -> None
        config_file_path = self.get_file_path(env)

        with config_file_path.open() as file_obj:
            self._config_dict = self.convert_config_dict(yaml.load(file_obj))


    def convert_config_dict(self, yaml_dict):
        # type: (Dict[str, Any]) -> Dict[str, Any]

        if not yaml_dict:
            return {'source_name': self.__class__.__name__}

        if 'cmdargs' in yaml_dict:
            # Care empty hash, because it becomes None.
            yaml_dict.setdefault('cmdargs', {})

            cmdargs_dict = yaml_dict['cmdargs']

            if 'severity' in cmdargs_dict:
                severity_name = cmdargs_dict['severity'].upper()
                severity = getattr(Level, severity_name, None)

                if not severity:
                    ConfigFileSource._warn_invalid_severity(severity_name)
                    return yaml_dict

                cmdargs_dict['severity'] = severity

        yaml_dict['source_name'] = self.__class__.__name__
        return yaml_dict


    @classmethod
    def _warn_invalid_severity(cls, severity_name):
        # type: (str) -> None
        possible_severities = ', '.join([possible_severity.name.lower()
                                         for possible_severity
                                         in list(Level)])

        logging.warning(('Severity `{severity_name}` is invalid. ' +
                         'Possible: {possible_severities}').format(
                             severity_name=severity_name,
                             possible_severities=possible_severities))


    def get_file_path(self, env):
        # type: (Dict[str, Any]) -> Path
        raise NotImplementedError()


    def get_config_dict(self):
        # type: () -> Dict[str, Any]
        return self._config_dict
