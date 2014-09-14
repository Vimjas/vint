from functools import reduce
from vint.linting.config.config_source import ConfigSource



class ConfigContainer(ConfigSource):
    def __init__(self, *config_sources):
        self.config_sources = config_sources


    def get_config_dict(self):
        def extends_deeply(dict_to_extend, prior_dict):
            for key, value in prior_dict.items():
                if isinstance(value, dict):
                    if key in dict_to_extend:
                        extends_deeply(dict_to_extend[key], value)
                    else:
                        dict_to_extend[key] = value
                else:
                    dict_to_extend[key] = value

            return dict_to_extend


        config_dicts_ordered_by_prior_asc = [config_source.get_config_dict()
                                             for config_source in self.config_sources]

        return reduce(extends_deeply, config_dicts_ordered_by_prior_asc, {})
