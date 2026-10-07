import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Interview Analyzer",
    layout="wide"
)

st.title("AI Interview Analyzer")


# ============================================================
# SETTINGS
# ============================================================

MAX_QUESTIONS = 5


# ============================================================
# SESSION STATE
# ============================================================

# Current interview question
if "current_question" not in st.session_state:
    st.session_state["current_question"] = "Tell me about yourself."


# Complete interview history
if "interview_history" not in st.session_state:
    st.session_state["interview_history"] = []


# Latest speech rate
if "speech_rate" not in st.session_state:
    st.session_state["speech_rate"] = "--"


# Latest filler-word count
if "filler_words" not in st.session_state:
    st.session_state["filler_words"] = "--"


# Latest transcript
if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""


# Latest Librosa features
if "audio_features" not in st.session_state:
    st.session_state["audio_features"] = None


# Latest Nemotron analysis
if "answer_analysis" not in st.session_state:
    st.session_state["answer_analysis"] = None


# Interview completion state
if "interview_complete" not in st.session_state:
    st.session_state["interview_complete"] = False


# ============================================================
# PAGE LAYOUT
# ============================================================

interview, metrics = st.columns([2, 1])


# ============================================================
# LEFT SIDE - INTERVIEW
# ============================================================

with interview:

    st.subheader("Interview")


    # --------------------------------------------------------
    # DISPLAY PREVIOUS CONVERSATION
    # --------------------------------------------------------

    for round_data in st.session_state["interview_history"]:

        with st.chat_message("assistant"):
            st.write(
                round_data["question"]
            )

        with st.chat_message("user"):
            st.write(
                round_data["transcript"]
            )


    # --------------------------------------------------------
    # ACTIVE INTERVIEW
    # --------------------------------------------------------

    if not st.session_state["interview_complete"]:

        question = st.session_state["current_question"]


        # Display current question
        with st.chat_message("assistant"):
            st.write(question)


        # Show question number
        current_number = (
            len(st.session_state["interview_history"]) + 1
        )

        st.caption(
            f"Question {current_number} of {MAX_QUESTIONS}"
        )


        # Candidate records answer
        audio = st.audio_input(
            "Record candidate response",
            key=f"audio_{current_number}"
        )


        # ----------------------------------------------------
        # SEND AUDIO TO FASTAPI
        # ----------------------------------------------------

        if audio is not None:

            files = {
                "audio": (
                    audio.name,
                    audio.getvalue(),
                    audio.type
                )
            }


            try:

                with st.spinner(
                    "Analyzing candidate response..."
                ):

                    response = requests.post(
                        "http://127.0.0.1:8000/interview/audio",

                        data={
                            "question": question
                        },

                        files=files,

                        timeout=120
                    )


                # ------------------------------------------------
                # SUCCESSFUL BACKEND RESPONSE
                # ------------------------------------------------

                if response.status_code == 200:

                    data = response.json()


                    # Store latest result
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


                    # --------------------------------------------
                    # SAVE COMPLETED INTERVIEW ROUND
                    # --------------------------------------------

                    interview_round = {

                        "question":
                            question,

                        "transcript":
                            data["transcript"],

                        "speech_rate":
                            data["speech_rate"],

                        "filler_words":
                            data["filler_words"],

                        "answer_analysis":
                            data["answer_analysis"]
                    }


                    st.session_state[
                        "interview_history"
                    ].append(
                        interview_round
                    )


                    # --------------------------------------------
                    # DECIDE WHETHER INTERVIEW CONTINUES
                    # --------------------------------------------

                    if (
                        len(
                            st.session_state[
                                "interview_history"
                            ]
                        )
                        < MAX_QUESTIONS
                    ):

                        # Nemotron follow-up becomes next question
                        st.session_state[
                            "current_question"
                        ] = (
                            data[
                                "answer_analysis"
                            ][
                                "follow_up_question"
                            ]
                        )

                    else:

                        st.session_state[
                            "interview_complete"
                        ] = True


                    # Reload Streamlit with next question
                    st.rerun()


                # ------------------------------------------------
                # BACKEND ERROR
                # ------------------------------------------------

                else:

                    st.error(
                        f"Backend error: "
                        f"{response.status_code}"
                    )

                    st.write(
                        response.text
                    )


            # ----------------------------------------------------
            # CONNECTION ERROR
            # ----------------------------------------------------

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI backend."
                )


            except requests.exceptions.Timeout:

                st.error(
                    "The analysis took too long. "
                    "Please try again."
                )


    # ========================================================
    # INTERVIEW COMPLETE
    # ========================================================

    else:

        st.success(
            "Interview completed."
        )

        st.write(
            f"You answered "
            f"{len(st.session_state['interview_history'])} "
            f"questions."
        )


# ============================================================
# RIGHT SIDE - HR METRICS
# ============================================================

with metrics:

    st.subheader("Live Analysis")


    # --------------------------------------------------------
    # SPEECH METRICS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # ANSWER ANALYSIS
    # --------------------------------------------------------

    analysis = (
        st.session_state["answer_analysis"]
    )


    if analysis is not None:

        st.divider()

        st.subheader(
            "Latest Answer Analysis"
        )


        st.write(
            "**Relevance**"
        )

        st.write(
            analysis["relevance"]
        )


        st.write(
            "**Clarity**"
        )

        st.write(
            analysis["clarity"]
        )


        st.write(
            "**Key Strengths**"
        )

        for strength in analysis["key_strengths"]:

            st.write(
                f"• {strength}"
            )


        st.write(
            "**Weak Points**"
        )

        for weakness in analysis["weak_points"]:

            st.write(
                f"• {weakness}"
            )


        st.write(
            "**Follow-up Question**"
        )

        st.write(
            analysis["follow_up_question"]
        )


        st.write(
            "**Overall Assessment**"
        )

        st.write(
            analysis["overall_assessment"]
        )