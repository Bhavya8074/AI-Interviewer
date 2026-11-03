import soundfile as sf
from kokoro import KPipeline

print("Loading Kokoro model...")

pipeline = KPipeline(lang_code="a")

text = "Hello, welcome to your AI interview. I will be your interviewer today."

generator = pipeline(text, voice="af_heart")

for i, (gs, ps, audio) in enumerate(generator):
    filename = f"kokoro_test_{i}.wav"
    sf.write(filename, audio, 24000)
    print("Audio saved:", filename)

print("Kokoro test completed!")