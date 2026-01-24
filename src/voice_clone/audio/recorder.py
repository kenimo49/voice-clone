"""Audio recording functionality."""

import queue
import sys
import threading
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

from ..config import AudioConfig


class Recorder:
    """Audio recorder for capturing voice samples."""

    def __init__(self, config: Optional[AudioConfig] = None, device: Optional[int] = None):
        self.config = config or AudioConfig()
        self.device = device
        self._audio_queue: queue.Queue = queue.Queue()
        self._recording = False
        self._recorded_frames: list[np.ndarray] = []

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"Recording status: {status}", file=sys.stderr)
        self._audio_queue.put(indata.copy())

    def record_fixed(self, duration: float, output_path: Path) -> Path:
        """Record audio for a fixed duration.

        Args:
            duration: Recording duration in seconds
            output_path: Path to save the recorded audio

        Returns:
            Path to the saved audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Recording for {duration} seconds...")
        print("Speak now!")

        audio_data = sd.rec(
            int(duration * self.config.sample_rate),
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            device=self.device,
        )
        sd.wait()

        print("Recording finished.")

        sf.write(
            output_path,
            audio_data,
            self.config.sample_rate,
            format=self.config.format,
            subtype=self.config.subtype,
        )

        return output_path

    def record_interactive(self, output_path: Path) -> Path:
        """Record audio interactively (Enter to start/stop).

        Args:
            output_path: Path to save the recorded audio

        Returns:
            Path to the saved audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._recorded_frames = []
        self._recording = False

        print("Press Enter to start recording...")
        input()

        print("Recording... Press Enter to stop.")
        self._recording = True

        stop_event = threading.Event()

        def wait_for_stop():
            input()
            stop_event.set()

        stop_thread = threading.Thread(target=wait_for_stop, daemon=True)
        stop_thread.start()

        with sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            device=self.device,
            callback=self._audio_callback,
        ):
            while not stop_event.is_set():
                try:
                    data = self._audio_queue.get(timeout=0.1)
                    self._recorded_frames.append(data)
                except queue.Empty:
                    continue

        self._recording = False
        print("Recording stopped.")

        if self._recorded_frames:
            audio_data = np.concatenate(self._recorded_frames, axis=0)
            sf.write(
                output_path,
                audio_data,
                self.config.sample_rate,
                format=self.config.format,
                subtype=self.config.subtype,
            )
            duration = len(audio_data) / self.config.sample_rate
            print(f"Saved {duration:.2f} seconds of audio to {output_path}")
        else:
            raise RuntimeError("No audio data recorded")

        return output_path

    def test_recording(self, duration: float = 1.0) -> bool:
        """Test if recording works.

        Args:
            duration: Test duration in seconds

        Returns:
            True if recording works, False otherwise
        """
        try:
            audio_data = sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=self.config.dtype,
                device=self.device,
            )
            sd.wait()

            if audio_data is None or len(audio_data) == 0:
                return False

            max_amplitude = np.max(np.abs(audio_data))
            return max_amplitude > 0.001

        except Exception as e:
            print(f"Recording test failed: {e}", file=sys.stderr)
            return False
