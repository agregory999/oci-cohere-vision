# OCI Cohere Vision Lab

Local Streamlit app for asking [Cohere Command A Vision](https://docs.oracle.com/en-us/iaas/Content/generative-ai/cohere-command-a-vision-07-2025.htm) questions about PNG and JPEG images through OCI Generative AI Inference. It supports guided analysis prompts and free-form questions; images and responses remain in session memory unless you download an answer.

## Quick start

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), OCI credentials configured outside this repository, and Generative AI inference access to a compartment.

```sh
uv sync --all-groups
cp run/.env.example run/.env
# Set OCI_COMPARTMENT_ID in run/.env (never commit it).
./run/local.sh
```

Open <http://localhost:8501>, upload a PNG/JPEG (up to 5 MB), choose or write a question, and select **Analyze image**. Submitting an image sends it and the question to OCI and makes a billable inference request.

The defaults are `us-chicago-1` and `cohere.command-a-vision`. API keys, security tokens, and OCI configuration stay outside the repository. See [run/README.md](run/README.md) for configuration and every supported run option.

## Develop

```sh
uv run pytest
uv run ruff check .
uv run python scripts/check_project.py .
```

Tests make no live OCI calls. See [architecture](docs/architecture.md), [OCI requirements](docs/requirements.md), and [contribution guidance](CONTRIBUTING.md) for durable project details. Report security issues privately as described in [SECURITY.md](SECURITY.md).
