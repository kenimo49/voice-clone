"""Vosk-based Speech-to-Text for voice-clone."""

import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

# Vosk model URLs
VOSK_MODELS = {
    "ja": {
        "name": "vosk-model-small-ja-0.22",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip",
    },
    "en": {
        "name": "vosk-model-small-en-us-0.15",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    },
    "zh": {
        "name": "vosk-model-small-cn-0.22",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip",
    },
}

DEFAULT_MODEL_DIR = Path.home() / ".voice-clone" / "models"


class VoskSTT:
    """Vosk-based Speech-to-Text engine."""

    def __init__(
        self,
        language: str = "ja",
        model_path: Optional[Path] = None,
    ) -> None:
        """Initialize Vosk STT.

        Args:
            language: Language code (ja, en, zh).
            model_path: Custom path to Vosk model directory.
        """
        self.language = language
        self._model = None
        self._model_path = model_path

        if self._model_path is None:
            model_info = VOSK_MODELS.get(language, VOSK_MODELS["ja"])
            self._model_path = DEFAULT_MODEL_DIR / model_info["name"]

    def _ensure_model(self) -> None:
        """Ensure model is downloaded and loaded."""
        if self._model is not None:
            return

        if not self._model_path.exists():
            print(f"Vosk model not found. Downloading for '{self.language}'...")
            download_model(self.language)

        self._load_model()

    def _load_model(self) -> None:
        """Load Vosk model."""
        try:
            from vosk import Model, SetLogLevel

            # Suppress Vosk logs
            SetLogLevel(-1)

            print(f"Loading Vosk model from {self._model_path}...")
            self._model = Model(str(self._model_path))
            print("Vosk model loaded.")

        except ImportError:
            print("Error: vosk not installed. Run: pip install vosk", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error loading Vosk model: {e}", file=sys.stderr)
            raise

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file.

        Returns:
            Transcribed text.
        """
        self._ensure_model()

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load audio file
        audio_data, sample_rate = sf.read(audio_path)

        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        # Convert to float32
        audio_data = audio_data.astype(np.float32)

        # Resample to 16kHz if needed (Vosk works best at 16kHz)
        if sample_rate != 16000:
            import scipy.signal as signal

            samples = int(len(audio_data) * 16000 / sample_rate)
            audio_data = signal.resample(audio_data, samples)
            sample_rate = 16000

        # Convert to PCM16 bytes
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()

        # Transcribe
        from vosk import KaldiRecognizer

        recognizer = KaldiRecognizer(self._model, sample_rate)
        recognizer.AcceptWaveform(audio_bytes)
        result = json.loads(recognizer.FinalResult())

        text = result.get("text", "")
        return text

    @property
    def is_available(self) -> bool:
        """Check if engine is available."""
        return self._model is not None or self._model_path.exists()


def download_model(language: str = "ja", target_dir: Optional[Path] = None) -> Path:
    """Download Vosk model for specified language.

    Args:
        language: Language code (ja, en, zh).
        target_dir: Target directory for model.

    Returns:
        Path to downloaded model directory.
    """
    import requests

    if language not in VOSK_MODELS:
        raise ValueError(f"Unsupported language: {language}. Supported: {list(VOSK_MODELS.keys())}")

    model_info = VOSK_MODELS[language]
    model_name = model_info["name"]
    url = model_info["url"]

    if target_dir is None:
        target_dir = DEFAULT_MODEL_DIR

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    model_path = target_dir / model_name

    if model_path.exists():
        print(f"Model already exists: {model_path}")
        return model_path

    print(f"Downloading Vosk model from {url}...")
    print("This may take a few minutes...")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Get total size for progress
    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunks = []

    for chunk in response.iter_content(chunk_size=8192):
        chunks.append(chunk)
        downloaded += len(chunk)
        if total_size:
            percent = (downloaded / total_size) * 100
            print(f"\rDownloading: {percent:.1f}%", end="", flush=True)

    print("\nExtracting...")

    content = b"".join(chunks)
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        zf.extractall(target_dir)

    print(f"Model downloaded to: {model_path}")
    return model_path
