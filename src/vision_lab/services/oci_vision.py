import base64
import time
import warnings
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import oci
from PIL import Image, UnidentifiedImageError

from ..config import LabError, Settings
from ..prompts import SYSTEM_PROMPT

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 25_000_000


@dataclass(frozen=True)
class ImageInfo:
    mime_type: str
    width: int
    height: int


@dataclass(frozen=True)
class Result:
    text: str
    elapsed: float
    model: str
    region: str
    finish_reason: str
    request_id: str


def validate_image(data: bytes) -> ImageInfo:
    if not data or len(data) > MAX_BYTES:
        raise LabError("Choose a nonempty PNG or JPEG no larger than 5 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as img:
                if img.format not in {"PNG", "JPEG"}:
                    raise LabError("Only PNG and JPEG images are supported.")
                if img.width * img.height > MAX_PIXELS:
                    raise LabError("Resize this image to 25 megapixels or less.")
                info = ImageInfo(Image.MIME[img.format], img.width, img.height)
                img.verify()
            with Image.open(BytesIO(data)) as img:
                img.load()
        return info
    except LabError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError,
            Image.DecompressionBombWarning, Image.DecompressionBombError) as from_error:
        raise LabError("This image cannot be decoded. Export it as a PNG or JPEG and try again.") from from_error


def make_client(settings: Settings) -> Any:
    """Construct the OCI inference client only when an analysis is submitted."""
    try:
        config = oci.config.from_file(str(Path(settings.config_file).expanduser()), settings.profile)
        config["region"] = settings.region
        signer = None
        if config.get("security_token_file"):
            token = Path(config["security_token_file"]).expanduser().read_text().strip()
            key = oci.signer.load_private_key_from_file(
                str(Path(config["key_file"]).expanduser()), config.get("pass_phrase"))
            signer = oci.auth.signers.SecurityTokenSigner(token, key)
        kwargs = {"signer": signer} if signer else {}
        return oci.generative_ai_inference.GenerativeAiInferenceClient(
            config, timeout=(10, 120), retry_strategy=oci.retry.NoneRetryStrategy(), **kwargs)
    except Exception as exc:
        raise LabError("Could not load OCI credentials. Check your config file, profile, and key; "
                       "refresh your OCI session if using session authentication.") from exc


def analyze_image(
    data: bytes, question: str, settings: Settings, client: Any | None = None
) -> Result:
    settings.validate()
    info = validate_image(data)
    if not question.strip():
        raise LabError("Enter a question before analyzing the image.")
    if len(question) > 8000:
        raise LabError("Keep your question under 8,000 characters.")
    m = oci.generative_ai_inference.models
    request = m.ChatDetails(
        compartment_id=settings.compartment_id,
        serving_mode=m.OnDemandServingMode(model_id=settings.model_id),
        chat_request=m.CohereChatRequestV2(
            is_stream=False, max_tokens=1500, temperature=0.2,
            messages=[
                m.CohereSystemMessageV2(content=[m.CohereTextContentV2(text=SYSTEM_PROMPT)]),
                m.CohereUserMessageV2(content=[
                    m.CohereTextContentV2(text=question.strip()),
                    m.CohereImageContentV2(image_url=m.CohereImageUrlV2(
                        url=f"data:{info.mime_type};base64,{base64.b64encode(data).decode('ascii')}")),
                ]),
            ]))
    client = client if client is not None else make_client(settings)
    started = time.monotonic()
    try:
        response = client.chat(request)
    except oci.exceptions.ServiceError as exc:
        messages = {
            401: "OCI authentication failed. Check your API key or refresh your session.",
            403: "OCI denied access. Check Generative AI inference permissions in your compartment.",
            404: "Model or compartment unavailable. Check Chicago access, model ID, and compartment permissions.",
            429: "OCI is rate limiting requests. Wait briefly and submit again.",
            400: "OCI rejected the request. Check the configured model and image; verify model availability in Chicago.",
        }
        raise LabError(messages.get(exc.status, "OCI could not complete the request. Try again shortly.")) from exc
    except Exception as exc:
        raise LabError("Could not reach OCI or the request timed out. Check your connection and try again.") from exc
    chat = response.data.chat_response
    if getattr(chat, "finish_reason", None) == "ERROR":
        raise LabError("The model could not complete this answer. Try another question or image.")
    content = getattr(getattr(chat, "message", None), "content", None) or []
    text = "\n\n".join(part.text for part in content
                       if getattr(part, "type", None) == "TEXT" and getattr(part, "text", None))
    if not text:
        raise LabError("OCI returned no answer text. Try a different question.")
    return Result(text, time.monotonic() - started, settings.model_id, settings.region,
                  getattr(chat, "finish_reason", "") or "", response.headers.get("opc-request-id", ""))
