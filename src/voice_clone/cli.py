"""CLI commands for voice-clone."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .config import AudioConfig, TTSConfig, get_default_config

console = Console()


@click.group()
@click.version_option()
def main():
    """Voice Clone - Qwen3-TTS based voice cloning tool."""
    pass


@main.command()
@click.option("-o", "--output", required=True, type=click.Path(), help="Output file path")
@click.option("-d", "--duration", type=float, default=None, help="Recording duration in seconds")
@click.option("--interactive", is_flag=True, help="Interactive mode (Enter to start/stop)")
@click.option("--device", type=int, default=None, help="Audio device index")
@click.option("--list-devices", is_flag=True, help="List available audio devices")
@click.option("--sample-rate", type=int, default=24000, help="Sample rate (default: 24000)")
def record(
    output: str,
    duration: Optional[float],
    interactive: bool,
    device: Optional[int],
    list_devices: bool,
    sample_rate: int,
):
    """Record audio for voice cloning.

    Examples:

        voice-clone record -o samples/speaker.wav -d 5

        voice-clone record -o samples/speaker.wav --interactive

        voice-clone record --list-devices
    """
    if list_devices:
        _show_audio_devices()
        return

    if not duration and not interactive:
        console.print("[red]Error:[/red] Specify --duration or --interactive")
        raise SystemExit(1)

    from .audio.recorder import Recorder

    config = AudioConfig(sample_rate=sample_rate)
    recorder = Recorder(config=config, device=device)

    output_path = Path(output)

    try:
        if interactive:
            recorder.record_interactive(output_path)
        else:
            recorder.record_fixed(duration, output_path)

        console.print(f"[green]Saved:[/green] {output_path}")

    except Exception as e:
        console.print(f"[red]Recording failed:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("-r", "--reference", required=True, type=click.Path(exists=True), help="Reference audio file")
@click.option("-t", "--text", required=True, help="Text to synthesize")
@click.option("-o", "--output", required=True, type=click.Path(), help="Output file path")
@click.option("--ref-text", default=None, help="Text spoken in reference audio (improves accuracy)")
@click.option("--auto-transcribe", is_flag=True, help="Auto-transcribe reference audio using Vosk")
@click.option("--device", type=click.Choice(["auto", "cpu", "cuda"]), default="auto", help="Compute device")
@click.option("--model", default="Qwen/Qwen3-TTS-12Hz-0.6B-Base", help="Model name")
@click.option("--sample-rate", type=int, default=24000, help="Output sample rate")
@click.option("--temperature", type=float, default=1.0, help="Sampling temperature (1.2-1.5: high tension, 0.7-0.9: calm)")
def generate(
    reference: str,
    text: str,
    output: str,
    ref_text: Optional[str],
    auto_transcribe: bool,
    device: str,
    model: str,
    sample_rate: int,
    temperature: float,
):
    """Generate speech using voice cloning.

    Examples:

        voice-clone generate -r samples/speaker.wav -t "Hello world" -o outputs/hello.wav

        voice-clone generate -r samples/speaker.wav -t "Test" -o outputs/test.wav --device cpu

        voice-clone generate -r samples/speaker.wav -t "Hi!" -o outputs/hi.wav --temperature 1.3

        voice-clone generate -r samples/speaker.wav --ref-text "Reference speech" -t "New text" -o outputs/out.wav

        voice-clone generate -r samples/speaker.wav --auto-transcribe -t "New text" -o outputs/out.wav
    """
    from .tts.qwen_tts import QwenTTS

    config = TTSConfig(model_name=model, device=device)
    tts = QwenTTS(config=config)

    reference_path = Path(reference)
    output_path = Path(output)

    # Auto-transcribe reference audio if requested
    if auto_transcribe and not ref_text:
        from .stt import VoskSTT

        console.print("[blue]Auto-transcribing reference audio...[/blue]")
        with console.status("[bold green]Transcribing..."):
            stt = VoskSTT(language="ja")
            ref_text = stt.transcribe(reference_path)

        if ref_text:
            console.print(f"[green]Transcribed:[/green] {ref_text}")
        else:
            console.print("[yellow]Warning:[/yellow] Could not transcribe reference audio")

    try:
        console.print(f"[blue]Reference:[/blue] {reference_path}")
        console.print(f"[blue]Text:[/blue] {text}")
        console.print(f"[blue]Device:[/blue] {device}")
        if ref_text:
            console.print(f"[blue]Ref Text:[/blue] {ref_text}")
        if temperature != 1.0:
            console.print(f"[blue]Temperature:[/blue] {temperature}")

        with console.status("[bold green]Generating speech..."):
            tts.generate(
                text=text,
                reference_audio=reference_path,
                output_path=output_path,
                sample_rate=sample_rate,
                ref_text=ref_text,
                temperature=temperature,
            )

        console.print(f"[green]Generated:[/green] {output_path}")

    except Exception as e:
        console.print(f"[red]Generation failed:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("-i", "--input", "input_file", required=True, type=click.Path(exists=True), help="Audio file to transcribe")
@click.option("-l", "--language", default="ja", type=click.Choice(["ja", "en", "zh"]), help="Language (default: ja)")
def transcribe(input_file: str, language: str):
    """Transcribe audio file to text using Vosk.

    Examples:

        voice-clone transcribe -i samples/speaker.wav

        voice-clone transcribe -i samples/english.wav -l en
    """
    from .stt import VoskSTT

    input_path = Path(input_file)

    try:
        console.print(f"[blue]Input:[/blue] {input_path}")
        console.print(f"[blue]Language:[/blue] {language}")

        with console.status("[bold green]Transcribing..."):
            stt = VoskSTT(language=language)
            text = stt.transcribe(input_path)

        if text:
            console.print(f"[green]Result:[/green] {text}")
        else:
            console.print("[yellow]No speech detected[/yellow]")

    except Exception as e:
        console.print(f"[red]Transcription failed:[/red] {e}")
        raise SystemExit(1)


@main.command("download-model")
@click.option("-l", "--language", default="ja", type=click.Choice(["ja", "en", "zh"]), help="Language (default: ja)")
def download_model(language: str):
    """Download Vosk STT model.

    Examples:

        voice-clone download-model

        voice-clone download-model -l en
    """
    from .stt import download_model as dl_model

    try:
        console.print(f"[blue]Downloading Vosk model for:[/blue] {language}")
        model_path = dl_model(language)
        console.print(f"[green]Model ready:[/green] {model_path}")

    except Exception as e:
        console.print(f"[red]Download failed:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("--audio", is_flag=True, help="Show audio devices")
@click.option("--gpu", is_flag=True, help="Show GPU information")
def devices(audio: bool, gpu: bool):
    """Show available devices.

    Examples:

        voice-clone devices --audio

        voice-clone devices --gpu

        voice-clone devices --audio --gpu
    """
    if not audio and not gpu:
        audio = True
        gpu = True

    if audio:
        _show_audio_devices()

    if gpu:
        if audio:
            console.print()
        _show_gpu_info()


def _show_audio_devices():
    """Display audio devices in a table."""
    from .audio.devices import list_audio_devices, get_default_device

    devices = list_audio_devices()
    default_input = get_default_device(input_device=True)
    default_output = get_default_device(input_device=False)

    table = Table(title="Audio Devices")
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Name", style="white")
    table.add_column("Type", style="green")
    table.add_column("Sample Rate", style="yellow", justify="right")
    table.add_column("Default", style="magenta")

    for d in devices:
        types = []
        if d.is_input:
            types.append("Input")
        if d.is_output:
            types.append("Output")

        default_marks = []
        if default_input and d.index == default_input.index:
            default_marks.append("Input")
        if default_output and d.index == default_output.index:
            default_marks.append("Output")

        table.add_row(
            str(d.index),
            d.name,
            "/".join(types),
            f"{int(d.default_samplerate)} Hz",
            ", ".join(default_marks) if default_marks else "",
        )

    console.print(table)


def _show_gpu_info():
    """Display GPU information."""
    from .audio.devices import get_gpu_info

    info = get_gpu_info()

    table = Table(title="GPU Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("CUDA Available", "Yes" if info["cuda_available"] else "No")
    table.add_row("Device Count", str(info["device_count"]))

    if info["devices"]:
        for gpu in info["devices"]:
            table.add_row(f"GPU {gpu['index']}", gpu["name"])
            table.add_row(f"  Memory", f"{gpu['total_memory_gb']:.1f} GB")
    else:
        table.add_row("Note", "CPU mode will be used")

    console.print(table)


if __name__ == "__main__":
    main()
