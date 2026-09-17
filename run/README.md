# Run locally

Local execution is the only supported deployment mode. The app uses your existing OCI API-key
profile or OCI CLI security-token session; it does not create or modify OCI resources.

## Configure and start

From the repository root:

```sh
uv sync --all-groups
cp run/.env.example run/.env
# Edit run/.env and set OCI_COMPARTMENT_ID.
./run/local.sh
```

The launcher validates `OCI_COMPARTMENT_ID`, loads `run/.env`, and starts Streamlit at
`http://127.0.0.1:8501` by default. It is safe to rerun: it creates no OCI resources and keeps
uploads and answers in session memory. Stop it with `Ctrl-C`.

## Configuration

`run/.env` is a sourceable shell file. `OCI_COMPARTMENT_ID` is required; the OCI profile,
config-file path, region, model ID, host, and port are optional. Use `VISION_LAB_ENV_FILE` to
select another local configuration file, for example:

```sh
VISION_LAB_ENV_FILE="$PWD/run/demo.env" ./run/local.sh
```

Do not commit any copied configuration file. OCI credentials, keys, security tokens, tenancy
IDs, compartment IDs, images, prompts, and responses must stay outside the repository.

## Deployment and build

Container builds and OCI deployment are intentionally unsupported. A hosted deployment would
need an explicit design for workload identity, network and Load Balancer ownership, authentication,
retention, and observability before adding scripts or infrastructure.
