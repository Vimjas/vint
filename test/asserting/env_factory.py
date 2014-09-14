from pathlib import Path


def env_factory(prior_env=None):
    preset_env = {
        'cwd': Path('path', 'to', 'project'),
        'cmd_args': {
            'verbose': True,
        },
        'home_path': Path('/', 'home', 'vint'),
        'file_paths': [
            '1.vim',
            '2.vim',
            '3.vim',
        ],
    }

    if prior_env is None:
        return preset_env

    preset_env.update(prior_env)
    return preset_env
