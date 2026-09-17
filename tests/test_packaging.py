"""Regression coverage for the documented Streamlit launch workflow."""

import subprocess
import sys
from pathlib import Path


def test_project_package_is_importable_outside_the_repository(tmp_path: Path) -> None:
    """The installed app must resolve imports when Streamlit executes its script."""
    result = subprocess.run(
        [sys.executable, "-I", "-c", "from vision_lab.client import analyze_image"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
