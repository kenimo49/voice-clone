"""Qwen3-TTS wrapper for voice cloning."""

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
import torch

from ..config import TTSConfig


class QwenTTS:
    """Wrapper for Qwen3-TTS voice cloning model."""

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._model = None
        self._device = None

    def _detect_device(self) -> str:
        """Detect the best available device."""
        if self.config.device != "auto":
            return self.config.device

        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def load_model(self) -> None:
        """Load the TTS model."""
        if self._model is not None:
            return

        self._device = self._detect_device()
        print(f"Loading model on {self._device}...")

        try:
            from qwen_tts import Qwen3TTSModel

            dtype = torch.float32
            if self._device == "cuda":
                dtype = torch.bfloat16

            self._model = Qwen3TTSModel.from_pretrained(
                self.config.model_name,
                device_map=self._device,
                dtype=dtype,
            )

            print(f"Model loaded: {self.config.model_name}")

        except Exception as e:
            print(f"Error loading model: {e}", file=sys.stderr)
            raise

    def generate(
        self,
        text: str,
        reference_audio: Path,
        output_path: Path,
        sample_rate: int = 24000,
        ref_text: Optional[str] = None,
    ) -> Path:
        """Generate speech using voice cloning.

        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio for voice cloning
            output_path: Path to save generated audio
            sample_rate: Output sample rate
            ref_text: Reference text (what was spoken in reference audio)

        Returns:
            Path to the generated audio file
        """
        self.load_model()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        reference_audio = Path(reference_audio)
        if not reference_audio.exists():
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

        print(f"Generating speech for: '{text}'")
        print(f"Using reference: {reference_audio}")

        # Load reference audio
        ref_audio_data, ref_sr = sf.read(reference_audio)
        if len(ref_audio_data.shape) > 1:
            ref_audio_data = ref_audio_data.mean(axis=1)
        ref_audio_data = ref_audio_data.astype(np.float32)

        # Generate using voice clone
        wavs, sr = self._model.generate_voice_clone(
            text=text,
            language="auto",
            ref_audio=(ref_audio_data, ref_sr),
            ref_text=ref_text,
            x_vector_only_mode=(ref_text is None),
        )

        audio = wavs[0]

        # Resample if needed
        if sr != sample_rate:
            import scipy.signal as signal
            samples = int(len(audio) * sample_rate / sr)
            audio = signal.resample(audio, samples)
            sr = sample_rate

        sf.write(output_path, audio, sr)
        duration = len(audio) / sr
        print(f"Generated {duration:.2f} seconds of audio to {output_path}")

        return output_path

    def generate_batch(
        self,
        texts: list[str],
        reference_audio: Path,
        output_dir: Path,
        sample_rate: int = 24000,
        prefix: str = "output",
        ref_text: Optional[str] = None,
    ) -> list[Path]:
        """Generate multiple audio files from a list of texts.

        Args:
            texts: List of texts to synthesize
            reference_audio: Path to reference audio
            output_dir: Directory to save generated audio
            sample_rate: Output sample rate
            prefix: Filename prefix
            ref_text: Reference text

        Returns:
            List of paths to generated audio files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        outputs = []
        for i, text in enumerate(texts):
            output_path = output_dir / f"{prefix}_{i:03d}.wav"
            self.generate(text, reference_audio, output_path, sample_rate, ref_text)
            outputs.append(output_path)

        return outputs

    @property
    def device(self) -> str:
        """Get the current device."""
        if self._device is None:
            return self._detect_device()
        return self._device
