#!/usr/bin/env python3
"""Check the repository's OCI Python project-standard baseline."""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_PATHS = (
    ".gitignore",
    ".oci-project.yml",
    "AGENTS.md",
    "README.md",
    "pyproject.toml",
    "run/.env.example",
    "run/README.md",
    "run/local.sh",
    "docs/architecture.md",
    "docs/requirements.md",
    "docs/decisions",
    "src/vision_lab/app.py",
    "src/vision_lab/services/oci_vision.py",
    "tests",
    "uv.lock",
)


def main(root: Path) -> int:
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    manifest = (root / ".oci-project.yml").read_text() if not missing else ""
    expected = ("standard_version: 1", "format: streamlit", 'python: ">=3.12"')
    invalid_manifest = [item for item in expected if item not in manifest]
    pyproject = (root / "pyproject.toml").read_text() if (root / "pyproject.toml").exists() else ""
    required_pyproject = ("requires-python = \">=3.12\"", "[dependency-groups]", "ruff")
    invalid_pyproject = [item for item in required_pyproject if item not in pyproject]
    run_env = (root / "run/.env.example").read_text() if (root / "run/.env.example").exists() else ""
    expected_run_env = ("# Required", "# Optional local", "# Optional container", "# Generic", "OCI_COMPARTMENT_ID")
    invalid_run_env = [item for item in expected_run_env if item not in run_env]
    local_script = root / "run/local.sh"
    executable = local_script.exists() and bool(local_script.stat().st_mode & 0o111)
    invalid_local_script = [] if executable else ["run/local.sh must be executable"]
    if missing or invalid_manifest or invalid_pyproject or invalid_run_env or invalid_local_script:
        for path in missing:
            print(f"missing required path: {path}")
        for item in invalid_manifest:
            print(f"invalid manifest: expected {item}")
        for item in invalid_pyproject:
            print(f"invalid pyproject: expected {item}")
        for item in invalid_run_env:
            print(f"invalid run environment example: expected {item}")
        for item in invalid_local_script:
            print(f"invalid run script: {item}")
        return 1
    print("OCI Python project standard check passed.")
    return 0


if __name__ == "__main__":
    project_root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    raise SystemExit(main(project_root))
