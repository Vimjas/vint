import yaml
import logging
from vint.linting.config.config_source import ConfigSource
from vint.linting.level import Level



class ConfigFileSource(ConfigSource):
    def __init__(self, env):
        config_file_path = self.get_file_path(env)

        with config_file_path.open() as file_obj:
            config_yaml = yaml.safe_load(file_obj)
            self._config_dict = self.convert_config_dict(config_yaml)


    def convert_config_dict(self, yaml_dict):
        if not yaml_dict:
            return {}

        if 'cmdargs' in yaml_dict:
            # Care empty hash, because it becomes None.
            if yaml_dict['cmdargs'] is None:
                yaml_dict['cmdargs'] = {}

            cmdargs_dict = yaml_dict['cmdargs']

            if 'severity' in cmdargs_dict:
                severity_name = cmdargs_dict['severity'].upper()
                severity = getattr(Level, severity_name, None)

                if not severity:
                    self._warn_invalid_severity(severity_name)
                    return yaml_dict

                cmdargs_dict['severity'] = severity

        return yaml_dict


    def _warn_invalid_severity(self, severity_name):
        possible_severities = ', '.join([possible_severity.name.lower()
                                         for possible_severity
                                         in list(Level)])

        logging.warning(('Severity `{severity_name}` is invalid. ' +
                         'Possible: {possible_severities}').format(
                             severity_name=severity_name,
                             possible_severities=possible_severities))


    def get_file_path(self, env):
        raise NotImplementedError()


    def get_config_dict(self):
        return self._config_dict
