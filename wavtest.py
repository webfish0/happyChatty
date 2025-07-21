from pyannote.audio import Pipeline
pipe = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="your_HF_token")
pipe.to("mps")        # fall back to "cpu" if mps isn’t available
print(pipe("demo.wav"))   # any 16-kHz mono (or stereo) WAV works
