from lib.linting.config.config_source import ConfigSource
from lib.linting.level import Level


class ConfigCmdargsSource(ConfigSource):
    def __init__(self, env):
        super().__init__(env)
        self._config_dict = self.build_config_dict(env)


    def build_config_dict(self, env):
        config_dict = {'cmdargs': {}}

        config_dict = self.normalize_verbose(env, config_dict)
        config_dict = self.normalize_severity(env, config_dict)
        config_dict = self.normalize_max_violations(env, config_dict)

        return config_dict


    def pass_config_by_key(self, key, env, config_dict):
        env_cmdargs = env['cmdargs']
        config_dict_cmdargs = config_dict['cmdargs']

        if key in env_cmdargs:
            config_dict_cmdargs[key] = env_cmdargs[key]

        return config_dict


    def normalize_verbose(self, env, config_dict):
        return self.pass_config_by_key('verbose', env, config_dict)


    def normalize_max_violations(self, env, config_dict):
        return self.pass_config_by_key('max-violations', env, config_dict)


    def normalize_severity(self, env, config_dict):
        env_cmdargs = env['cmdargs']
        config_dict_cmdargs = config_dict['cmdargs']

        # Severity option priority is:
        #   1. error
        #   2. warning
        #   3. style problem
        if 'style' in env_cmdargs:
            config_dict_cmdargs['severity'] = Level.STYLE_PROBLEM

        if 'warning' in env_cmdargs:
            config_dict_cmdargs['severity'] = Level.WARNING

        if 'error' in env_cmdargs:
            config_dict_cmdargs['severity'] = Level.ERROR

        return config_dict


    def get_config_dict(self):
        return self._config_dict
