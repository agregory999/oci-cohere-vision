# Architecture

## Boundaries

`src/vision_lab/app.py` is the Streamlit UI boundary. It owns page layout, widget state,
and the local `.env` convenience load. `src/vision_lab/services/oci_vision.py` owns image
validation, OCI client construction, request building, and response parsing. `config.py`
resolves non-secret runtime settings, while `prompts.py` contains the guided task text.

The UI calls the service only after the user submits an image and question. OCI clients are
not created at import time, so a refreshed local session can be used on the next submission.
The `vision_lab.client` module remains a compatibility re-export for existing Python callers.
`run/local.sh` is the supported local entry point: it sources `run/.env`, validates the required
configuration, and starts Streamlit. The application reads that environment at runtime; a root
`.env` is supported only as a legacy local convenience fallback.

## OCI interaction and access boundary

The service calls OCI Generative AI Inference using the Cohere Chat API v2 and an on-demand
model in the configured region. The application is a local, single-user dashboard; it does
not offer authentication, a public endpoint, or a separately consumed API. That access
boundary is why Streamlit is the selected format. There is no OCI container deployment option,
Dockerfile, or infrastructure automation in this repository.

## Data sensitivity and retention

Images, prompts, answers, and OCI request IDs can be sensitive. The app holds uploads and
answers in Streamlit session memory and does not write them to disk. On Analyze, it sends the
image and question to the selected OCI Generative AI endpoint. OCI credentials are loaded from
the user's local OCI configuration or security-token session and never rendered or logged.

## Errors and observability

The service maps expected OCI status failures to safe, actionable messages and avoids exposing
response payloads, credentials, or configuration details. The UI displays non-secret request
metadata (model, region, elapsed time, finish reason, and request ID) after success. Local
operators should use OCI Audit and service logs for platform-level observability; this app does
not emit image contents or prompts to application logs. The app does not cache OCI clients,
uploads, or responses beyond the active Streamlit session.
