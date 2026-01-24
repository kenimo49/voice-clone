"""Speech-to-Text module for voice-clone."""

from .vosk_stt import VoskSTT, download_model

__all__ = ["VoskSTT", "download_model"]
