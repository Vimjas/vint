from vint.linting.config.config_source import ConfigSource
from vint.linting.level import Level


class ConflictedOptionsError(Exception):
    def __init__(self, conflicted_option_names):
        self.conflicted_option_names = conflicted_option_names

    def __str__(self):
        option_names = ', '.join(self.conflicted_option_names)
        return 'These options are conflicted: {0}'.format(option_names)


class ConfigCmdargsSource(ConfigSource):
    def __init__(self, env):
        self._config_dict = self._build_config_dict(env)


    def get_config_dict(self):
        return self._config_dict


    def _build_config_dict(self, env):
        config_dict = {'cmdargs': {}}

        config_dict = self._normalize_color(env, config_dict)
        config_dict = self._normalize_json(env, config_dict)
        config_dict = self._normalize_stat(env, config_dict)
        config_dict = self._normalize_verbose(env, config_dict)
        config_dict = self._normalize_severity(env, config_dict)
        config_dict = self._normalize_max_violations(env, config_dict)
        config_dict = self._normalize_format(env, config_dict)
        config_dict = self._normalize_env(env, config_dict)

        return config_dict


    def _pass_config_by_key(self, key, env, config_dict):
        env_cmdargs = env['cmdargs']
        config_dict_cmdargs = config_dict['cmdargs']

        if key in env_cmdargs and env_cmdargs[key] is not None:
            config_dict_cmdargs[key] = env_cmdargs[key]

        return config_dict


    def _normalize_stat(self, env, config_dict):
        return self._pass_config_by_key('stat', env, config_dict)


    def _normalize_json(self, env, config_dict):
        return self._pass_config_by_key('json', env, config_dict)


    def _normalize_color(self, env, config_dict):
        env_cmdargs = env['cmdargs']

        should_colorize = 'color' in env_cmdargs and env_cmdargs['color'] is not None
        should_not_colorize = 'no_color' in env_cmdargs and env_cmdargs['no_color'] is not None

        if should_colorize and should_not_colorize:
            raise ConflictedOptionsError(['color', 'no_color'])

        if should_colorize:
            config_dict['cmdargs']['color'] = True

        if should_not_colorize:
            config_dict['cmdargs']['color'] = False

        return config_dict


    def _normalize_verbose(self, env, config_dict):
        return self._pass_config_by_key('verbose', env, config_dict)


    def _normalize_max_violations(self, env, config_dict):
        return self._pass_config_by_key('max-violations', env, config_dict)


    def _normalize_format(self, env, config_dict):
        return self._pass_config_by_key('format', env, config_dict)


    def _normalize_severity(self, env, config_dict):
        env_cmdargs = env['cmdargs']
        config_dict_cmdargs = config_dict['cmdargs']

        # Severity option priority is:
        #   1. error
        #   2. warning
        #   3. style problem
        if env_cmdargs.get('style_problem', False):
            config_dict_cmdargs['severity'] = Level.STYLE_PROBLEM

        if env_cmdargs.get('warning', False):
            config_dict_cmdargs['severity'] = Level.WARNING

        if env_cmdargs.get('error', False):
            config_dict_cmdargs['severity'] = Level.ERROR

        return config_dict


    def _normalize_env(self, env, config_dict):
        env_cmdargs = env['cmdargs']
        config_dict_cmdargs = config_dict['cmdargs']

        if 'enable_neovim' in env_cmdargs and env_cmdargs['enable_neovim'] is True:
            config_dict_cmdargs['env'] = {'neovim': True}

        return config_dict
