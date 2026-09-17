import os
from dataclasses import dataclass


class LabError(Exception):
    """An actionable message safe to display to the user."""


@dataclass(frozen=True)
class Settings:
    compartment_id: str
    profile: str = "DEFAULT"
    config_file: str = "~/.oci/config"
    region: str = "us-chicago-1"
    model_id: str = "cohere.command-a-vision"

    @classmethod
    def from_env(cls) -> "Settings":
        names = {
            "compartment_id": "OCI_COMPARTMENT_ID",
            "profile": "OCI_CONFIG_PROFILE",
            "config_file": "OCI_CONFIG_FILE",
            "region": "OCI_GENAI_REGION",
            "model_id": "OCI_COHERE_VISION_MODEL_ID",
        }
        defaults = cls(compartment_id="")
        return cls(**{key: os.getenv(env, getattr(defaults, key)).strip()
                      for key, env in names.items()})

    def validate(self) -> None:
        if not self.compartment_id:
            raise LabError("Set OCI_COMPARTMENT_ID in .env, then restart the app.")
        if not self.region or not self.model_id or not self.profile:
            raise LabError("Region, model ID, and OCI profile must not be empty. Check .env.")
