import os.path

def get_fixture_path(filename):
    return os.path.join('test', 'fixture', 'ast', filename)
