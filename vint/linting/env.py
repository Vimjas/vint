import os
import os.path
from argparse import ArgumentParser



def build_environment(argv):
    env = {}
    parser = ArgumentParser(prog='vint', description='Lint Vim script')

    parser.add_argument('-v', '--verbose', action='store_true', help='output verbose message')
    parser.add_argument('-e', '--error', action='store_true', help='report only errors')
    parser.add_argument('-w', '--warning', action='store_true', help='report errors and warnings')
    parser.add_argument('-s', '--style-problem', action='store_true', help='report errors, warnings and style problems')
    parser.add_argument('-m', '--max-violations', type=int, help='limit max violations count')
    parser.add_argument('files', nargs='*', help='file or directory path to lint')
    namespace = parser.parse_args(argv)

    cmdargs = vars(namespace)
    env['cmdargs'] = cmdargs

    print(cmdargs)

    found_files = set()
    _collect_file(cmdargs['files'], result=found_files)
    env['file_paths'] = found_files

    env['cwd'] = os.getcwd()

    return env


def _collect_file(file_paths, result):
    for file_path in file_paths:
        if os.path.isdir(file_path):
            _collect_file_from_dir(file_path, result)
        else:
            result.add(file_path)


def _collect_file_from_dir(dir_path_to_search, result):
    for dir_path, sub_dir_names, file_names in os.walk(dir_path_to_search):
        for sub_dir_name in sub_dir_names:
            sub_dir_path = os.path.join(dir_path, sub_dir_name)

            _collect_file_from_dir(sub_dir_path, result)

        result.update([os.path.join(dir_path, file_name) for file_name in file_names])
