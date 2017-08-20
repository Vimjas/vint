import os
import os.path
from pathlib import Path
from vint.linting.file_filter import find_vim_script


def build_environment(cmdargs):
    return {
        'cmdargs': cmdargs,
        'home_path': _get_home_path(),
        'xdg_config_home': _get_xdg_config_home(),
        'cwd': _get_cwd(),
        'file_paths': _get_file_paths(cmdargs)
    }


def _get_cwd():
    return Path(os.getcwd())


def _get_home_path():
    return Path(os.path.expanduser('~'))


def _get_file_paths(cmdargs):
    if 'files' not in cmdargs:
        return []

    found_file_paths = find_vim_script(map(Path, cmdargs['files']))

    return set(found_file_paths)


def _get_xdg_config_home():
    return Path(os.environ.get(
        "XDG_CONFIG_HOME",
        str(_get_home_path().joinpath(".config"))
    ))
