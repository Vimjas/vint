from pathlib import Path


def get_asset_path(file_path):
    vint_pkg_root = Path(__file__).parent
    asset_dir = Path(vint_pkg_root, 'asset')

    return Path(asset_dir, file_path)
