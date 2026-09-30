import streamlit as st
import requests

st.set_page_config(
    page_title="AI Interview Analyzer",
    layout="wide"
)

if "speech_rate" not in st.session_state:
    st.session_state["speech_rate"] = "--"

if "filler_words" not in st.session_state:
    st.session_state["filler_words"] = "--"

if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""
    
st.title("AI Interview Analyzer")

interview, metrics = st.columns([2, 1])

# -------------------------
# LEFT SIDE - INTERVIEW
# -------------------------

with interview:

    st.subheader("Interview")

    with st.chat_message("assistant"):
        st.write("Tell me about yourself.")

    audio = st.audio_input(
        "Record candidate response"
    )

    # Send recorded audio to FastAPI
    if audio is not None:

        files = {
            "audio": (
                audio.name,
                audio.getvalue(),
                audio.type
            )
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/interview/audio",
                files=files
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state["transcript"] = data["transcript"]
                st.session_state["speech_rate"] = data["speech_rate"]
                st.session_state["filler_words"] = data["filler_words"]

                st.success("Audio analyzed successfully")

                with st.chat_message("user"):
                    st.write(data["transcript"])

            else:
                st.error(
                    f"Backend error: {response.status_code}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to FastAPI backend."
            )


# -------------------------
# RIGHT SIDE - HR METRICS
# -------------------------

with metrics:

    st.subheader("Live Analysis")

    speech_rate = st.session_state["speech_rate"]
    filler_words = st.session_state["filler_words"]

    if speech_rate == "--":
        st.metric("Speech Rate", "--")
    else:
        st.metric(
            "Speech Rate",
            f"{speech_rate} WPM"
        )

    st.metric(
        "Filler Words",
        filler_words
    )