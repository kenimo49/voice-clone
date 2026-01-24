"""Audio device management for WSL/Linux."""

from dataclasses import dataclass
from typing import Optional

import sounddevice as sd


@dataclass
class AudioDevice:
    """Audio device information."""

    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    is_input: bool
    is_output: bool

    def __str__(self) -> str:
        type_str = []
        if self.is_input:
            type_str.append("Input")
        if self.is_output:
            type_str.append("Output")
        return f"[{self.index}] {self.name} ({'/'.join(type_str)}) - {int(self.default_samplerate)}Hz"


def list_audio_devices() -> list[AudioDevice]:
    """List all available audio devices."""
    devices = []
    for idx, device in enumerate(sd.query_devices()):
        devices.append(
            AudioDevice(
                index=idx,
                name=device["name"],
                max_input_channels=device["max_input_channels"],
                max_output_channels=device["max_output_channels"],
                default_samplerate=device["default_samplerate"],
                is_input=device["max_input_channels"] > 0,
                is_output=device["max_output_channels"] > 0,
            )
        )
    return devices


def list_input_devices() -> list[AudioDevice]:
    """List input devices only."""
    return [d for d in list_audio_devices() if d.is_input]


def list_output_devices() -> list[AudioDevice]:
    """List output devices only."""
    return [d for d in list_audio_devices() if d.is_output]


def get_default_device(input_device: bool = True) -> Optional[AudioDevice]:
    """Get the default input or output device."""
    try:
        if input_device:
            idx = sd.default.device[0]
            if idx is None:
                idx = sd.query_devices(kind="input")["name"]
                devices = list_input_devices()
                for d in devices:
                    if d.name == idx:
                        return d
                return devices[0] if devices else None
        else:
            idx = sd.default.device[1]
            if idx is None:
                idx = sd.query_devices(kind="output")["name"]
                devices = list_output_devices()
                for d in devices:
                    if d.name == idx:
                        return d
                return devices[0] if devices else None

        devices = list_audio_devices()
        for d in devices:
            if d.index == idx:
                return d
        return None
    except Exception:
        devices = list_input_devices() if input_device else list_output_devices()
        return devices[0] if devices else None


def get_device_by_index(index: int) -> Optional[AudioDevice]:
    """Get a device by its index."""
    devices = list_audio_devices()
    for d in devices:
        if d.index == index:
            return d
    return None


def get_gpu_info() -> dict:
    """Get GPU information for TTS."""
    info = {
        "cuda_available": False,
        "device_count": 0,
        "devices": [],
    }

    try:
        import torch

        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["device_count"] = torch.cuda.device_count()
            for i in range(info["device_count"]):
                props = torch.cuda.get_device_properties(i)
                info["devices"].append(
                    {
                        "index": i,
                        "name": props.name,
                        "total_memory_gb": props.total_memory / (1024**3),
                    }
                )
    except ImportError:
        pass

    return info
