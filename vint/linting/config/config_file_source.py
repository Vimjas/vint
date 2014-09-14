import yaml
from vint.linting.config.config_source import ConfigSource
from vint.linting.level import Level



class ConfigFileSource(ConfigSource):
    def __init__(self, env):
        config_file_path = self.get_file_path(env)

        with config_file_path.open() as file_obj:
            self._config_dict = self.convert_config_dict(yaml.load(file_obj))


    def convert_config_dict(self, yaml_dict):
        if not yaml_dict:
            return {}

        if 'cmdargs' in yaml_dict:
            cmdargs_dict = yaml_dict['cmdargs']
            if 'severity' in cmdargs_dict:
                cmdargs_dict['severity'] = Level[cmdargs_dict['severity'].upper()]

        return yaml_dict


    def get_file_path(self, env):
        raise NotImplementedError()


    def get_config_dict(self):
        return self._config_dict
