# Project context

- UI boundary: `src/vision_lab/app.py`; OCI API construction and inference stay in `src/vision_lab/services/oci_vision.py`.
- Use `run/local.sh` for local execution; it loads `run/.env`. The root `.env` remains a legacy local-only fallback.
- Safe development: `uv sync --all-groups`, then `./run/local.sh`.
- Verify with `uv run pytest`, `uv run ruff check .`, and `uv run python scripts/check_project.py .`.
- Never commit `.env`, OCI config files, tenancy or compartment identifiers, security tokens, or private keys. Uploaded images and model responses must remain in session memory unless a user explicitly downloads an answer.
