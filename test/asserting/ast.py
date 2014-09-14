from pathlib import Path


def get_fixture_path(filename):
    return Path('test', 'fixture', 'ast', filename)
