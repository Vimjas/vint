import os
import os.path
from pathlib import Path
from argparse import ArgumentParser



def build_environment(argv):
    env = {}
    env = _set_cmdargs(env, argv)
    env = _set_file_paths(env, argv)
    env = _set_cwd(env, argv)
    env = _set_home_path(env, argv)

    return env


def _set_cwd(env, argv):
    if 'cwd' in env:
        return env

    env['cwd'] = Path(os.getcwd())
    return env


def _set_home_path(env, argv):
    if 'home_path' in env:
        return env

    env['home_path'] = Path(os.path.expanduser('~'))
    return env


def _set_cmdargs(env, argv):
    if 'cmdargs' in env:
        return env

    parser = ArgumentParser(prog='vint', description='Lint Vim script')

    parser.add_argument('-v', '--verbose', action='store_true', help='output verbose message')
    parser.add_argument('-e', '--error', action='store_true', help='report only errors')
    parser.add_argument('-w', '--warning', action='store_true', help='report errors and warnings')
    parser.add_argument('-s', '--style-problem', action='store_true', help='report errors, warnings and style problems')
    parser.add_argument('-m', '--max-violations', type=int, help='limit max violations count')
    parser.add_argument('-c', '--color', action='store_true', help='colorize output when possible')
    parser.add_argument('-j', '--json', action='store_true', help='output json style')
    parser.add_argument('files', nargs='*', help='file or directory path to lint')
    namespace = parser.parse_args(argv)

    cmdargs = vars(namespace)
    env['cmdargs'] = cmdargs
    return env


def _set_file_paths(env, argv):
    if 'file_paths' in env:
        return env

    env_with_cmdargs = _set_cmdargs(env, argv)
    cmdargs = env_with_cmdargs['cmdargs']

    found_files = _collect_files([Path(path) for path in cmdargs['files']])

    env_with_cmdargs['file_paths'] = found_files
    return env_with_cmdargs


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
