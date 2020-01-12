from typing import Dict, Any  # noqa: F401
from functools import reduce
from vint.linting.config.config_source import ConfigSource


class ConfigEmptyEntryException(BaseException):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'empty entry in config: `{path}`'.format(path=self.path)


def merge_dict_deeply(posterior, prior, path=[]):
    def try_get(obj, path):
        if obj is None:
            raise ConfigEmptyEntryException(".".join(path))
        return obj

    # type: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
    tmp = {}

    for key in set(posterior.keys()) | set(prior.keys()):
        child_path = path + [key]
        if key in prior:
            if isinstance(prior[key], dict):
                child_posterior = try_get(posterior.get(key, {}), child_path)
                tmp[key] = merge_dict_deeply(child_posterior, prior[key],
                                             child_path)
            else:
                tmp[key] = try_get(prior[key], child_path)
        else:
            if isinstance(posterior[key], dict):
                tmp[key] = try_get(posterior[key], child_path).copy()
            else:
                tmp[key] = try_get(posterior[key], child_path)

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
