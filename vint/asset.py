from pathlib import Path

_asset_dir = Path(Path(__file__).parent, 'asset')


def get_asset_path(file_path):
    return Path(_asset_dir, file_path)
