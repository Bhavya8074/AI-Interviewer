
from kokoro import KPipeline
import soundfile as sf
import numpy as np
from io import BytesIO

# Load Kokoro only once and reuse it
pipeline = None


def get_pipeline():
    global pipeline

    if pipeline is None:
        print("Loading Kokoro voice model...")
        pipeline = KPipeline(lang_code="a")

    return pipeline


def generate_speech(text: str, voice: str = "af_heart") -> bytes:

    if not text or not text.strip():
        raise ValueError("Speech text cannot be empty.")

    kokoro = get_pipeline()

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
