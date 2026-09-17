"""Compatibility exports for the OCI Vision service adapter."""

from .services.oci_vision import (
    MAX_BYTES,
    MAX_PIXELS,
    ImageInfo,
    Result,
    analyze_image,
    make_client,
    validate_image,
)

__all__ = [
    "MAX_BYTES",
    "MAX_PIXELS",
    "ImageInfo",
    "Result",
    "analyze_image",
    "make_client",
    "validate_image",
]
