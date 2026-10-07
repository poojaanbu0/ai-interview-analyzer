import streamlit as st
import requests


st.set_page_config(
    page_title="AI Interview Analyzer",
    layout="wide"
)


# -------------------------
# SESSION STATE
# -------------------------

if "speech_rate" not in st.session_state:
    st.session_state["speech_rate"] = "--"

if "filler_words" not in st.session_state:
    st.session_state["filler_words"] = "--"

if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""

if "audio_features" not in st.session_state:
    st.session_state["audio_features"] = None

if "answer_analysis" not in st.session_state:
    st.session_state["answer_analysis"] = None


# -------------------------
# PAGE
# -------------------------

st.title("AI Interview Analyzer")

interview, metrics = st.columns([2, 1])


# Current interview question
question = "Tell me about yourself."


# -------------------------
# LEFT SIDE - INTERVIEW
# -------------------------

with interview:

    st.subheader("Interview")

    with st.chat_message("assistant"):
        st.write(question)

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

                data={
                    "question": question
                },

                files=files
            )


            if response.status_code == 200:

                data = response.json()

                st.session_state["transcript"] = (
                    data["transcript"]
                )

                st.session_state["speech_rate"] = (
                    data["speech_rate"]
                )

                st.session_state["filler_words"] = (
                    data["filler_words"]
                )

                st.session_state["audio_features"] = (
                    data["audio_features"]
                )

                st.session_state["answer_analysis"] = (
                    data["answer_analysis"]
                )

                st.success(
                    "Audio analyzed successfully"
                )


                # Candidate transcript
                with st.chat_message("user"):
                    st.write(
                        data["transcript"]
                    )


                # Temporary debugging
                st.write(
                    "Extracted Audio Features"
                )

                st.json(
                    data["audio_features"]
                )


            else:

                st.error(
                    f"Backend error:  {response.status_code}"
                )

                st.write(response.text)


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI backend."
            )


# -------------------------
# RIGHT SIDE - HR METRICS
# -------------------------

with metrics:

    st.subheader("Live Analysis")

    speech_rate = (
        st.session_state["speech_rate"]
    )

    filler_words = (
        st.session_state["filler_words"]
    )


    if speech_rate == "--":

        st.metric(
            "Speech Rate",
            "--"
        )

    else:

        st.metric(
            "Speech Rate",
            f"{speech_rate} WPM"
        )


    st.metric(
        "Filler Words",
        filler_words
    )


    # -------------------------
    # NEMOTRON ANALYSIS
    # -------------------------

    analysis = (
        st.session_state["answer_analysis"]
    )

    if analysis is not None:

        st.divider()

        st.subheader("Answer Analysis")

        st.write("**Relevance**")
        st.write(
            analysis["relevance"]
        )

        st.write("**Clarity**")
        st.write(
            analysis["clarity"]
        )

        st.write("**Key Strengths**")

        for strength in analysis["key_strengths"]:
            st.write(
                f"• {strength}"
            )

        st.write("**Weak Points**")

        for weakness in analysis["weak_points"]:
            st.write(
                f"• {weakness}"
            )

        st.write("**Follow-up Question**")
        st.write(
            analysis["follow_up_question"]
        )

        st.write("**Overall Assessment**")
        st.write(
            analysis["overall_assessment"]
        )