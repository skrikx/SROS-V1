import subprocess
import sys


def test_version_parity_script_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_version_parity.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
