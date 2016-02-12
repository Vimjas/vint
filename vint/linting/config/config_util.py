def get_config_value(config_dict, keys, default=None):
    inner_dict = config_dict

    for key in keys[:-1]:
        if key not in inner_dict:
            return default

        inner_dict = inner_dict[key]

    return inner_dict.get(keys[-1], default)
