import os
import subprocess
import sys
from pathlib import Path

import pytest

vital_dir = Path("test", "fixture", "cli", "vital.vim")


@pytest.mark.skipif(
    not os.path.exists(str(vital_dir / "autoload")),
    reason="vital.vim submodule not checked out",
)
def test_survive_after_linting():
    """Test that it handles vital.vim, without crashing."""
    cmd = [sys.executable, "-m", "vint", vital_dir]
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True
        )
    except subprocess.CalledProcessError as err:
        output = err.stdout
    assert "Traceback" not in output
