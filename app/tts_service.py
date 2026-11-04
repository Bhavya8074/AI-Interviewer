
from io import BytesIO
from threading import Lock
import sys

# Load Kokoro only once and reuse it
pipeline = None
_pipeline_lock = Lock()
_pipeline_state = "not_started"


def get_pipeline():
    global pipeline, _pipeline_state

    if pipeline is not None:
        return pipeline

    with _pipeline_lock:
        if pipeline is not None:
            return pipeline
        _pipeline_state = "loading"
        try:
            from kokoro import KPipeline
            print("Loading Kokoro voice model...")
            pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
            _pipeline_state = "ready"
        except ImportError as exc:
            _pipeline_state = "unavailable"
            raise RuntimeError(
                "Kokoro could not import a required speech package: "
                f"{exc}. Install or repair the speech dependencies with "
                f"'{sys.executable} -m pip install -r requirements.txt'. "
                f"The server is running with {sys.executable}."
            ) from exc
        except Exception:
            _pipeline_state = "unavailable"
            raise

    return pipeline


def preload_pipeline():
    """Warm Kokoro in the background so the first question can speak sooner."""
    try:
        get_pipeline()
    except Exception as exc:
        print(f"Kokoro voice warmup failed: {exc}")


def get_pipeline_state() -> str:
    return _pipeline_state


def generate_speech(text: str, voice: str = "af_heart") -> bytes:

    if not text or not text.strip():
        raise ValueError("Speech text cannot be empty.")

    kokoro = get_pipeline()
    import numpy as np
    import soundfile as sf

    generator = kokoro(
        text.strip(),
        voice=voice
    )

    audio_chunks = []

    for _, _, audio in generator:
        audio_chunks.append(audio)

    if not audio_chunks:
        raise RuntimeError("Kokoro did not generate audio.")

    # Combine all generated audio chunks
    final_audio = np.concatenate(audio_chunks)

    # Convert audio into WAV bytes
    audio_buffer = BytesIO()

    sf.write(
        audio_buffer,
        final_audio,
        24000,
        format="WAV"
    )

    audio_buffer.seek(0)

    return audio_buffer.getvalue()
