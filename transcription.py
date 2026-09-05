from faster_whisper import WhisperModel


def transcribe_audio(audio_path):

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False
    )

    transcript_parts = []

    for segment in segments:

        text = segment.text.strip()

        if not text:
            continue

        transcript_parts.append(text)

    # Keep Whisper's segment boundaries.
    # This is extremely important for MoM generation.
    transcript = ". ".join(transcript_parts)

    if transcript and not transcript.endswith((".", "?", "!")):
        transcript += "."

    return transcript