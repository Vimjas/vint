import re

VIM_SCRIPT_FILE_NAME_PATTERNS = r'(?:^[\._]g?vimrc$|.*\.vim$)'


def find_vim_script(file_paths):
    vim_script_file_paths = []

    for file_path in file_paths:
        if file_path.is_dir():
            vim_script_file_paths += _find_vim_script_into_dir(file_path)
            continue

        vim_script_file_paths.append(file_path)

    return vim_script_file_paths


def _find_vim_script_into_dir(dir_path):
    if not dir_path.is_dir():
        return []

    vim_script_file_paths = []

    for file_path in dir_path.iterdir():
        if _is_vim_script(file_path):
            vim_script_file_paths.append(file_path)
            continue

        if file_path.is_dir():
            vim_script_file_paths += _find_vim_script_into_dir(file_path)
            continue

    return vim_script_file_paths


def _is_vim_script(file_path):
    if not file_path.is_file():
        return False

    file_name = file_path.name
    return bool(re.match(VIM_SCRIPT_FILE_NAME_PATTERNS, file_name))
