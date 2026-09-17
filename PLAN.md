# OCI Cohere Vision Lab — Project Plan

## Purpose

Build a small local Python web app that makes Cohere Command A Vision in OCI Chicago tangible. A user selects a local image, chooses a guided inference task or writes their own question, submits it to OCI Generative AI, and gets a clean, reusable answer.

The app demonstrates **vision-language inference**, not deterministic object detection: it explains and reasons about an image, chart, or document in response to an instruction. For coordinates, confidence-scored fixed labels, and bulk detection, OCI Vision remains the complementary service.

## First release

### User journey

1. Open the local app in a browser.
2. Upload a PNG or JPEG from the computer (maximum 5 MB).
3. See a local preview and basic file details; the image is held in browser/session memory only.
4. Choose one guided task or enter a free-form question.
5. Click **Analyze image**.
6. See the answer, request metadata, a copy button, and any response citations/details the model returns.

### Guided tasks

| Task | Example instruction | Demonstrates |
| --- | --- | --- |
| Describe and summarize | "Describe what is visible. Separate direct observations from reasonable inferences." | General visual understanding |
| Inspect for issues | "Identify visible safety, quality, or operational issues. For each, explain the visual evidence and uncertainty." | Operational review / anomaly triage |
| Extract a structured inventory | "Return JSON with visible items: name, count when evident, location description, and notes." | Structured extraction without claiming detector-grade precision |
| Analyze a chart or document | "Extract the key values and conclusions. Flag anything illegible or uncertain." | Charts and document insight |

Free-form questions always remain available, including multi-turn follow-ups against the same uploaded image in a later increment.

### Result presentation

- Answer rendered as readable Markdown, with a one-click copy action.
- Clear sections for **Answer**, **Request details** (model, region, elapsed time), and **Raw response** (collapsible).
- Distinct error states for missing OCI credentials, wrong region/model access, oversized/unsupported image, and API failures.
- A lightweight privacy note: images are sent only to the selected OCI Generative AI endpoint when Analyze is pressed; the application does not persist uploaded files or responses by default.

## Technical design

### Stack

- **Python 3.12+**, **Streamlit** for the single-screen local UI, the official **OCI Python SDK**, and `uv` for dependency management.
- `us-chicago-1` as the default region; `cohere.command-a-vision` as the default model ID.
- OCI Generative AI Inference's Cohere **Chat API v2** with a base64-encoded PNG/JPEG input.
- Standard OCI configuration from `~/.oci/config` / profile, with environment-variable overrides for the compartment OCID, profile, region, model, and optional serving endpoint.

### Modules

```text
oci-cohere-vision/
  src/vision_lab/
    app.py                # Streamlit screen and interaction state
    config.py             # Validated settings and OCI configuration
    prompts.py            # Guided prompts and structured-output instructions
    services/oci_vision.py # Cohere Chat API v2 adapter
  tests/
    test_prompts.py
    test_config.py
    test_client.py        # Mocked OCI SDK client
  .env.example            # No secrets; documents required variables
  pyproject.toml
  uv.lock
  README.md               # Setup, IAM, run instructions, troubleshooting
```

The UI calls a narrow `analyze_image(image_bytes, mime_type, question, settings)` function. This keeps OCI code testable and makes it easy to add a FastAPI service later without rewriting inference logic.

### Configuration

Required:

```text
OCI_COMPARTMENT_ID=<your compartment OCID>
```

Defaults/overrides:

```text
OCI_CONFIG_PROFILE=DEFAULT
OCI_GENAI_REGION=us-chicago-1
OCI_COHERE_VISION_MODEL_ID=cohere.command-a-vision
OCI_GENAI_SERVING_ENDPOINT=<optional dedicated endpoint OCID>
```

On-demand is the intended default. If `OCI_GENAI_SERVING_ENDPOINT` is set, the client switches to that dedicated endpoint. No OCI private key, auth token, or compartment ID is ever displayed in the UI or committed to the repository.

### Request and response behavior

1. Validate content type and 5 MB size limit before the call.
2. Base64-encode the upload only in memory.
3. Send the selected prompt plus image via Cohere Chat API v2.
4. Capture response text and safe, non-secret metadata.
5. Render structured JSON as both formatted output and a raw copyable response; otherwise render Markdown/text.
6. Do not store source images or results. Optional local history can be a clearly labeled later feature.

## OCI prerequisites

- An OCI user/session configured locally with access to the target compartment.
- Generative AI permissions that allow inference calls in the compartment; validate exact tenancy IAM policy wording with the OCI administrator.
- Access to the Cohere Command A Vision model in Chicago. Chicago supports the model in on-demand and dedicated modes.
- Usage/cost awareness: image inputs are tokenized; Oracle documents that a 512×512 image is approximately 1,610 tokens. The UI should show image dimensions and a soft warning for large images, rather than present a misleading cost estimate.

## Build milestones

### Milestone 1 — Runnable demo

- Scaffold project, pinned dependencies, `.env.example`, and README.
- Implement local upload/preview, two guided prompts, free-form question, OCI authentication/configuration, and results display.
- Add mock-backed tests and a manual smoke-test checklist.

**Acceptance:** a user with valid OCI credentials and compartment ID can run `uv run streamlit run src/vision_lab/app.py`, upload a JPG/PNG, ask a question, and receive a displayed Command A Vision response from Chicago.

### Milestone 2 — Stronger demo experience

- Add all four guided task cards, structured-inventory JSON validation, copy/download response, elapsed time, and polished error messages.
- Add a clear API/settings panel that reveals only non-secret settings.

**Acceptance:** each task visibly changes the request intent; invalid files, absent config, and rejected OCI requests receive actionable guidance without leaking credentials.

### Milestone 3 — Optional extensions

- Conversation history for follow-up questions while retaining the image in the current session.
- Batch queue and CSV/JSON export for qualitative reviews (not a substitute for OCI Vision batch detection).
- Side-by-side OCI Vision result comparison for images where labels/bounding boxes matter.

## Decisions to keep explicit

- **Local-only first:** no database, object storage, user auth, or deployment in the first release.
- **Privacy default:** no persistence; uploads leave the machine only when the user requests inference.
- **Honest capability framing:** Command A Vision is used for semantic understanding and explanation. We will not market outputs as calibrated labels, numeric counts, or bounding boxes.
- **Target:** on-demand Chicago endpoint first; dedicated endpoint support is configuration-only.

## Validation plan

- Unit tests: configuration resolution, guided prompts, MIME/size validation, image encoding, and mocked response parsing.
- Manual tests: a photo, a dense document, a chart, an unsupported file, an oversized image, missing configuration, and a denied/failed OCI call.
- Review response quality on a small representative set before adopting any output format downstream—especially if it influences compliance, safety, or automated decisions.

## Sources

- OCI lists Cohere Command A Vision as available in US Midwest (Chicago) in both on-demand and dedicated modes: https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm
- Cohere Command A Vision supports multimodal image-plus-text inference and requires the Cohere Chat API v2: https://docs.oracle.com/en-us/iaas/Content/generative-ai/cohere-command-a-vision-07-2025.htm
