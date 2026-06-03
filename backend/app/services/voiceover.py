from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import math
import os
import re
import shutil
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ELEVENLABS_API_BASE = "https://api.elevenlabs.io"
DEFAULT_ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
VOICEOVER_TIMEOUT_SECONDS = 90


#[GenAI Usage] Prompt: Convert generated slide narration into speech for paper-summary videos using ElevenLabs text-to-speech.
#[GenAI Usage] LLM response begins

class VoiceoverError(Exception):
    pass


class VoiceoverConfigurationError(VoiceoverError):
    pass


class VoiceoverProviderError(VoiceoverError):
    pass


@dataclass(frozen=True)
class VoiceoverSegment:
    index: int
    slide_title: str
    text: str
    audio_path: str
    duration_seconds: float
    character_count: int


@dataclass(frozen=True)
class VoiceoverArtifact:
    provider: str
    voice_id: str
    model_id: str
    output_format: str
    combined_audio_path: str
    segments: list[VoiceoverSegment]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["segments"] = [asdict(segment) for segment in self.segments]
        return data


def generate_elevenlabs_voiceover(slides, output_dir: Path) -> VoiceoverArtifact:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise VoiceoverConfigurationError("ELEVENLABS_API_KEY is not configured.")

    output_dir.mkdir(parents=True, exist_ok=True)
    voice_id = os.getenv("ELEVENLABS_VOICE_ID") or _first_available_voice_id(api_key)
    model_id = os.getenv("ELEVENLABS_MODEL_ID", DEFAULT_ELEVENLABS_MODEL_ID)
    output_format = os.getenv("ELEVENLABS_OUTPUT_FORMAT", DEFAULT_ELEVENLABS_OUTPUT_FORMAT)

    segments: list[VoiceoverSegment] = []
    for index, slide in enumerate(slides, start=1):
        text = _clean_voiceover_text(slide.narration)
        audio_path = output_dir / f"voiceover_{index:02d}.mp3"
        _create_speech(
            api_key=api_key,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            text=text,
            audio_path=audio_path,
        )
        duration_seconds = _audio_duration_seconds(audio_path)
        segments.append(
            VoiceoverSegment(
                index=index,
                slide_title=slide.title,
                text=text,
                audio_path=str(audio_path),
                duration_seconds=duration_seconds,
                character_count=len(text),
            )
        )

    combined_audio_path = output_dir / "voiceover_combined.mp3"
    _combine_audio_segments(
        [Path(segment.audio_path) for segment in segments],
        combined_audio_path,
    )

    return VoiceoverArtifact(
        provider="elevenlabs",
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
        combined_audio_path=str(combined_audio_path),
        segments=segments,
    )


def voiceover_slide_durations(voiceover: VoiceoverArtifact) -> list[int]:
    return [
        max(2, math.ceil(segment.duration_seconds))
        for segment in voiceover.segments
    ]


def _first_available_voice_id(api_key: str) -> str:
    try:
        response = _request_json(
            "GET",
            f"{ELEVENLABS_API_BASE}/v1/voices",
            api_key=api_key,
        )
    except VoiceoverProviderError:
        return DEFAULT_ELEVENLABS_VOICE_ID

    voices = response.get("voices") if isinstance(response, dict) else None
    if not isinstance(voices, list):
        return DEFAULT_ELEVENLABS_VOICE_ID

    for voice in voices:
        if isinstance(voice, dict) and voice.get("voice_id"):
            return str(voice["voice_id"])

    return DEFAULT_ELEVENLABS_VOICE_ID


def _create_speech(
    *,
    api_key: str,
    voice_id: str,
    model_id: str,
    output_format: str,
    text: str,
    audio_path: Path,
) -> None:
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True,
        },
    }
    url = (
        f"{ELEVENLABS_API_BASE}/v1/text-to-speech/"
        f"{quote(voice_id)}?output_format={quote(output_format)}"
    )
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=VOICEOVER_TIMEOUT_SECONDS) as response:
            audio_bytes = response.read()
    except HTTPError as exc:
        detail = _read_error_detail(exc)
        raise VoiceoverProviderError(
            f"ElevenLabs voiceover generation failed with HTTP {exc.code}: {detail}"
        ) from exc
    except (TimeoutError, URLError, OSError) as exc:
        raise VoiceoverProviderError("ElevenLabs voiceover generation failed.") from exc

    if not audio_bytes:
        raise VoiceoverProviderError("ElevenLabs returned empty audio.")

    audio_path.write_bytes(audio_bytes)


def _request_json(method: str, url: str, *, api_key: str) -> dict:
    request = Request(
        url,
        headers={
            "xi-api-key": api_key,
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urlopen(request, timeout=VOICEOVER_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = _read_error_detail(exc)
        raise VoiceoverProviderError(
            f"ElevenLabs request failed with HTTP {exc.code}: {detail}"
        ) from exc
    except (TimeoutError, URLError, OSError, json.JSONDecodeError) as exc:
        raise VoiceoverProviderError("ElevenLabs request failed.") from exc


def _combine_audio_segments(segment_paths: list[Path], output_path: Path) -> None:
    if not segment_paths:
        raise VoiceoverProviderError("No voiceover audio segments were generated.")
    if len(segment_paths) == 1:
        shutil.copyfile(segment_paths[0], output_path)
        return

    ffmpeg_path = _ffmpeg_path()
    concat_path = output_path.parent / "voiceover_segments.txt"
    concat_path.write_text(
        "\n".join(f"file '{_ffmpeg_concat_path(path)}'" for path in segment_paths),
        encoding="utf-8",
    )

    _run_ffmpeg(
        [
            ffmpeg_path,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            str(output_path),
        ],
        "Combining ElevenLabs voiceover audio failed.",
    )


def _audio_duration_seconds(audio_path: Path) -> float:
    result = _run_ffmpeg(
        [
            _ffmpeg_path(),
            "-hide_banner",
            "-i",
            str(audio_path),
            "-f",
            "null",
            "-",
        ],
        "Reading ElevenLabs voiceover duration failed.",
        allow_nonzero=True,
    )
    output = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if not match:
        return 5.0

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return hours * 3600 + minutes * 60 + seconds


def _run_ffmpeg(
    command: list[str],
    failure_message: str,
    *,
    allow_nonzero: bool = False,
) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            command,
            check=not allow_nonzero,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise VoiceoverProviderError(failure_message) from exc
    return result


def _ffmpeg_path() -> str:
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise VoiceoverProviderError("imageio-ffmpeg is not installed.") from exc
    return imageio_ffmpeg.get_ffmpeg_exe()


def _clean_voiceover_text(text: str) -> str:
    clean_text = " ".join((text or "").split())
    if not clean_text:
        return "This slide introduces the next part of the paper summary."
    return clean_text[:4500]


def _ffmpeg_concat_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "'\\''")


def _read_error_detail(exc: HTTPError) -> str:
    try:
        detail = exc.read().decode("utf-8", errors="replace")
    except OSError:
        return "No error body returned."
    return detail[:500] if detail else "No error body returned."
