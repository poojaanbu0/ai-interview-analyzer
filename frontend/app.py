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

if "final_summary" not in st.session_state:
    st.session_state["final_summary"] = None

if "awaiting_hr_decision" not in st.session_state:
    st.session_state["awaiting_hr_decision"] = False

if "show_extra_question_form" not in st.session_state:
    st.session_state["show_extra_question_form"] = False

if "processed_audio_questions" not in st.session_state:
    st.session_state["processed_audio_questions"] = []


# ============================================================
# PAGE LAYOUT
# ============================================================

interview, metrics = st.columns([2, 1])


# ============================================================
# LEFT SIDE - INTERVIEW
# ============================================================

with interview:

    st.subheader("Interview")
    if (
    st.session_state["awaiting_hr_decision"]
    and not st.session_state["interview_complete"]
     ):

        st.divider()
        st.subheader("HR: Extend or Finish Interview")

        st.write(
            f"{len(st.session_state['interview_history'])} "
            "questions have been completed."
        )

        # Option 1: HR wants to add another question
        if st.button(
            "Add Extra Question",
            key="add_extra_question"
        ):
            st.session_state["show_extra_question_form"] = True

        # Display the question form only when requested
        if st.session_state["show_extra_question_form"]:

            extra_question = st.text_input(
                "Enter the additional interview question",
                key="extra_question_input",
                placeholder="e.g. Explain a technical challenge you solved."
            )

            if st.button(
                "Ask Candidate",
                key="ask_extra_question"
            ):

                if extra_question.strip():

                    st.session_state["current_question"] = (
                        extra_question.strip()
                    )

                    st.session_state["show_extra_question_form"] = False
                    st.session_state["awaiting_hr_decision"] = False

                    st.rerun()

                else:
                    st.warning("Please enter a question.")

        st.write("Or finish the interview and generate the report.")

        # Option 2: HR wants the final summary
        if st.button(
            "Generate Interview Summary",
            key="generate_final_summary"
        ):

            try:
                with st.spinner("Generating final interview summary..."):

                    response = requests.post(
                        "http://127.0.0.1:8000/interview/summary",
                        json={
                            "interview_history":
                                st.session_state["interview_history"]
                        },
                        timeout=120
                    )

                if response.status_code == 200:

                    summary_data = response.json()

                    st.session_state["final_summary"] = (
                        summary_data["interview_summary"]
                    )

                    st.session_state["interview_complete"] = True
                    st.session_state["awaiting_hr_decision"] = False

                    st.rerun()

                else:
                    st.error(
                        f"Summary API failed: {response.status_code}"
                    )
                    st.write(response.text)

            except requests.exceptions.RequestException as error:
                st.error(f"Could not generate summary: {error}")



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

    if (
    not st.session_state["interview_complete"]
    and not st.session_state["awaiting_hr_decision"]
     ):

        question = st.session_state["current_question"]


        # Display current question
        with st.chat_message("assistant"):
            st.write(question)


        # Show question number
        current_number = (
            len(st.session_state["interview_history"]) + 1
        )

        if current_number <= MAX_QUESTIONS:
            st.caption(f"Question {current_number} of {MAX_QUESTIONS}")
        else:
            st.caption(f"Extra Question {current_number - MAX_QUESTIONS}")


        # Candidate records answer
        audio = st.audio_input(
            "Record candidate response",
            key=f"audio_{current_number}"
        )


        # ----------------------------------------------------
        # SEND AUDIO TO FASTAPI
        # ----------------------------------------------------

        if (
        audio is not None
        and current_number not in st.session_state["processed_audio_questions"]
        ):

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

                    st.session_state["processed_audio_questions"].append(current_number)

                    # --------------------------------------------
                    # DECIDE WHETHER INTERVIEW CONTINUES
                    # --------------------------------------------

                    if len(st.session_state["interview_history"]) < MAX_QUESTIONS:

                        # Continue interview
                        st.session_state["current_question"] = (
                            data["answer_analysis"]["follow_up_question"]
                        )

                    else:

                        # Five or more questions completed.
                        # Wait for HR to decide what happens next.
                        st.session_state["awaiting_hr_decision"] = True

                        # Interview is complete
                        # st.session_state["interview_complete"] = True

                        # # Generate final interview summary
                        # summary_response = requests.post(
                        #     "http://127.0.0.1:8000/interview/summary",
                        #     json={
                        #         "interview_history":
                        #             st.session_state["interview_history"]
                        #     },
                        #     timeout=120
                        # )

                        # if summary_response.status_code == 200:

                        #     summary_data = summary_response.json()

                        #     st.session_state["final_summary"] = (
                        #         summary_data["interview_summary"]
                        #     )

                        # else:

                        #     st.session_state["final_summary"] = None

                        #     st.error(
                        #         "Could not generate the final interview summary."
                        #     )

                        #     st.write(
                        #         summary_response.text
                        #     )

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

    if st.session_state["interview_complete"]:
        st.success("Interview completed.")

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

        # --------------------------------------------------------
# FINAL INTERVIEW SUMMARY
# --------------------------------------------------------

if st.session_state["final_summary"] is not None:

    st.divider()
    st.subheader("Final Interview Summary")

    summary = st.session_state["final_summary"]

    st.write("**Overall Summary**")
    st.write(summary["overall_summary"])

    st.write("**Key Strengths**")
    for strength in summary["key_strengths"]:
        st.write(f"• {strength}")

    st.write("**Improvement Areas**")
    for area in summary["improvement_areas"]:
        st.write(f"• {area}")

    st.write("**Technical Topics**")
    for topic in summary["technical_topics"]:
        st.write(f"• {topic}")

    st.write("**Communication Observations**")
    for observation in summary["communication_observations"]:
        st.write(f"• {observation}")