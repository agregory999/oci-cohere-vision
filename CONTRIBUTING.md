# Contributing

## Before opening a pull request

1. Create a focused branch and keep OCI credentials, OCIDs, uploads, and model responses out of commits.
2. Keep Streamlit UI work in `src/vision_lab/app.py` and OCI integration in `src/vision_lab/services/oci_vision.py`.
3. Add or update tests for changed behavior.
4. Use `run/local.sh` with a copied `run/.env` for local execution, and run the checks below from the repository root.

```sh
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run python scripts/check_project.py .
```

## Pull requests

Explain the user-visible change, testing performed, and any OCI/IAM impact. Do not include real images, prompts, answers, OCI request IDs, compartment IDs, or credential material in issues, pull requests, screenshots, or logs.
