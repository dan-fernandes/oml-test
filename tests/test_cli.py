import subprocess
import sys

from oml_test import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "oml_test", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
