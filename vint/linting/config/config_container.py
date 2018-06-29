from typing import Dict, Any
from functools import reduce
from vint.linting.config.config_source import ConfigSource


def merge_dict_deeply(posterior, prior):
    # type: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
    tmp = {}

    for key in set(posterior.keys()) | set(prior.keys()):
        if key in prior:
            if isinstance(prior[key], dict):
                tmp[key] = merge_dict_deeply(posterior.get(key, {}), prior[key])
            else:
                tmp[key] = prior[key]
        else:
            if isinstance(posterior[key], dict):
                tmp[key] = posterior[key].copy()
            else:
                tmp[key] = posterior[key]

    return tmp


class ConfigContainer(ConfigSource):
    def __init__(self, *config_sources):
        self.config_sources = config_sources


    def get_config_dict(self):
        config_dicts_ordered_by_prior_asc = [config_source.get_config_dict()
                                             for config_source in self.config_sources]

        result = reduce(merge_dict_deeply, config_dicts_ordered_by_prior_asc, {})
        result['source_name'] = self.__class__.__name__

        return result
