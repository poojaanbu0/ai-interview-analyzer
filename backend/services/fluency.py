import re


FILLER_WORDS = [
    "um",
    "uh",
    "umm",
    "uhh",
    "hmm",
    "like",
    "actually",
    "basically"
]


def calculate_speech_rate(transcript: str, duration: float):

    words = transcript.split()
    word_count = len(words)

    if duration <= 0:
        return 0

    speech_rate = (word_count / duration) * 60

    return round(speech_rate, 2)


def count_filler_words(transcript: str):

    words = re.findall(
        r"\b[\w']+\b",
        transcript.lower()
    )

    filler_count = 0

    for word in words:
        if word in FILLER_WORDS:
            filler_count += 1

    return filler_count