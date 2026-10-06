import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError


# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    raise ValueError("NVIDIA_API_KEY not found in .env")


# -----------------------------------
# NVIDIA CLIENT
# -----------------------------------

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)


# -----------------------------------
# OUTPUT SCHEMA
# -----------------------------------

class InterviewAnalysis(BaseModel):
    relevance: str
    clarity: str
    key_strengths: list[str]
    weak_points: list[str]
    follow_up_question: str
    overall_assessment: str


# -----------------------------------
# INTERVIEW ANALYZER
# -----------------------------------

def analyze_interview(
    question: str,
    transcript: str,
    speech_rate: float,
    filler_words: int
) -> InterviewAnalysis:

    prompt = f"""
You are an AI interview answer analyzer.

Interview Question:
{question}

Candidate Answer:
{transcript}

Speech Metrics:
Speech Rate: {speech_rate} words per minute
Filler Words: {filler_words}

Analyze the content of the candidate's answer.

The speech metrics are supplemental information.
Do not infer personality, psychological confidence, intelligence,
or hiring suitability from speech rate or filler-word count.

Return ONLY valid JSON.

The JSON must follow exactly this structure:

{{
    "relevance": "short assessment",
    "clarity": "short assessment",
    "key_strengths": [
        "strength 1",
        "strength 2"
    ],
    "weak_points": [
        "weak point 1",
        "weak point 2"
    ],
    "follow_up_question": "one useful follow-up question",
    "overall_assessment": "short overall assessment"
}}

Rules:

- Return JSON only.
- Do not use Markdown.
- Do not wrap the JSON in ```json.
- Do not include text before or after the JSON.
- key_strengths must be an array of strings.
- weak_points must be an array of strings.
- Keep the analysis concise.
- Do not include reasoning or thinking steps.
- Do not make a hiring decision.
"""

    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an interview answer analyzer. "
                    "Return only valid JSON matching the requested structure."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,
        max_tokens=500,

        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    )

    # -----------------------------------
    # DEBUG INFORMATION
    # -----------------------------------

    print("\n----- API DEBUG -----")
    print(
        "Finish reason:",
        response.choices[0].finish_reason
    )
    print(
        "Token usage:",
        response.usage
    )

    # -----------------------------------
    # GET RAW MODEL RESPONSE
    # -----------------------------------

    raw_response = response.choices[0].message.content

    print("\n----- RAW NVIDIA RESPONSE -----")
    print(raw_response)

    # -----------------------------------
    # PARSE JSON
    # -----------------------------------

    try:
        parsed_json = json.loads(raw_response)

    except json.JSONDecodeError as error:
        print("\nInvalid JSON returned by Nemotron.")
        print(error)
        raise

    # -----------------------------------
    # VALIDATE WITH PYDANTIC
    # -----------------------------------

    try:
        validated_analysis = InterviewAnalysis(
            **parsed_json
        )

    except ValidationError as error:
        print("\nJSON structure validation failed.")
        print(error)
        raise

    return validated_analysis


