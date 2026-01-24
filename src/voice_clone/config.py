"""Configuration management for voice-clone."""

from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class AudioConfig:
    """Audio recording configuration."""

    sample_rate: int = 24000
    channels: int = 1
    dtype: str = "float32"
    format: str = "WAV"
    subtype: str = "PCM_16"


@dataclass
class TTSConfig:
    """TTS model configuration."""

    model_name: str = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
    device: str = "auto"  # "auto", "cpu", "cuda"
    torch_dtype: str = "float32"  # CPU requires float32


@dataclass
class Config:
    """Main configuration."""

    audio: AudioConfig = field(default_factory=AudioConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)

    samples_dir: Path = field(default_factory=lambda: Path("samples"))
    outputs_dir: Path = field(default_factory=lambda: Path("outputs"))

    def __post_init__(self):
        """Ensure directories exist."""
        self.samples_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_default_config() -> Config:
    """Get the default configuration."""
    root = get_project_root()
    return Config(
        samples_dir=root / "samples",
        outputs_dir=root / "outputs",
    )
