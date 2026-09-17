# Operational requirements

## OCI resources and IAM

- A target compartment and access to OCI Generative AI Inference in the selected region.
- The Cohere Command A Vision on-demand model must be available to the tenancy in that region.
- Grant the operating user or workload only the OCI Generative AI inference permission needed to
  submit inference requests in the target compartment. Do not grant tenancy-wide administration,
  Object Storage, or unrelated services for this application.
- Local API-key authentication requires the normal OCI config profile and its private key; OCI CLI
  security-token sessions are also supported. Keep those files outside this repository.

Confirm exact policy syntax with the tenancy administrator and the current OCI Generative AI IAM
documentation before deployment, because policy syntax and model availability can vary by tenancy
and region.

## Runtime configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `OCI_COMPARTMENT_ID` | Yes | Compartment used for inference requests. |
| `OCI_CONFIG_PROFILE` | No | OCI config profile; defaults to `DEFAULT`. |
| `OCI_CONFIG_FILE` | No | Local OCI config path; defaults to `~/.oci/config`. |
| `OCI_GENAI_REGION` | No | OCI region; defaults to `us-chicago-1`. |
| `OCI_COHERE_VISION_MODEL_ID` | No | On-demand model ID; defaults to `cohere.command-a-vision`. |

Copy `run/.env.example` to `run/.env` and place local values there. The root `.env` is a
legacy local-only fallback. Do not commit configuration, credentials,
security tokens, private keys, tenancy identifiers, or compartment identifiers.

## Deployment prerequisites

This project is designed for local deployment. Install Python 3.12 or newer and `uv`, configure
OCI authentication outside the repository, and set the required compartment variable. A future
hosted deployment must replace local OCI config-file authentication with an appropriate workload
identity and define its own network, authentication, retention, and logging controls.
