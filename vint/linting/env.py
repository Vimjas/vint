import os
import os.path
from pathlib import Path


def build_environment(cmdargs):
    return {
        'cmdargs': cmdargs,
        'home_path': _get_home_path(cmdargs),
        'cwd': _get_cwd(cmdargs),
        'file_paths': _get_file_paths(cmdargs)
    }


def _get_cwd(cmdargs):
    return Path(os.getcwd())


def _get_home_path(cmdargs):
    return Path(os.path.expanduser('~'))


def _get_file_paths(cmdargs):
    if 'files' not in cmdargs:
        return []

    found_files = _collect_files([Path(path) for path in cmdargs['files']])
    return found_files


def _collect_files(paths):
    result = set()
    for path in paths:
        if path.is_dir():
            dir_path = path
            result |= _collect_files(tuple(dir_path.iterdir()))

        else:
            file_path = path
            result.add(file_path)

    return result
