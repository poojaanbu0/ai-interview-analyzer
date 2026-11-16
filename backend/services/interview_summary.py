
import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError


load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    raise RuntimeError("NVIDIA_API_KEY is missing from the environment.")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
)


class FinalInterviewSummary(BaseModel):
    overall_summary: str
    key_strengths: list[str]
    improvement_areas: list[str]
    technical_topics: list[str]
    communication_observations: list[str]


def _generate_response(prompt: str, retry: bool = False) -> str:

    if retry:
        prompt += """

IMPORTANT:
Your previous response was not valid JSON.

Generate the complete summary again.
Return one valid JSON object.
Use double quotes for all JSON keys and string values.
Escape any double quotes inside string values.
Do not include Markdown or additional text.
"""

    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an interview summary assistant. "
                    "Summarize evidence from the completed interview. "
                    "Return only a valid JSON object."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=0.2,
        max_tokens=1200,

        response_format={
            "type": "json_object"
        },

        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    )

    raw = response.choices[0].message.content

    if not raw or not raw.strip():
        raise ValueError("The AI returned an empty summary.")

    return raw.strip()


def _parse_summary(raw_response: str) -> FinalInterviewSummary:

    # Remove Markdown code fences if the model includes them.
    cleaned = raw_response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "").strip()

    # Extract the JSON object if extra text surrounds it.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("No valid JSON object found in AI response.")

    cleaned = cleaned[start:end + 1]

    parsed_json = json.loads(cleaned)

    return FinalInterviewSummary.model_validate(parsed_json)


def generate_interview_summary(
    interview_history: list,
) -> FinalInterviewSummary:

    if not interview_history:
        raise ValueError("Interview history is empty.")

    interview_text = ""

    for index, round_data in enumerate(interview_history, start=1):

        interview_text += f"""
Interview Round {index}

Question:
{round_data["question"]}

Candidate Answer:
{round_data["transcript"]}

Answer Analysis:
{json.dumps(round_data["answer_analysis"], ensure_ascii=False)}

Speech Rate:
{round_data["speech_rate"]}

Filler Words:
{round_data["filler_words"]}

------------------------------
"""

    prompt = f"""
You are analyzing a completed interview.

Below is the complete interview history.

{interview_text}

Create a concise interview-level summary based only on
the evidence contained in the interview.

Return ONLY a valid JSON object with exactly this structure:

{{
    "overall_summary": "string",
    "key_strengths": ["string"],
    "improvement_areas": ["string"],
    "technical_topics": ["string"],
    "communication_observations": ["string"]
}}

Rules:

- Consider the entire interview, not only the final answer.
- Do not make a hiring decision.
- Do not output Hire, Reject, Select, or similar decisions.
- Do not infer personality, intelligence, psychological confidence,
  or other traits from speech metrics.
- Treat speech rate and filler-word count only as supplemental
  communication observations.
- Do not invent skills, experience, technologies, or achievements
  that were not present in the interview.
- Distinguish between something the candidate mentioned and
  something they demonstrated with specific details.
- Keep the summary concise.
- All values must follow the specified JSON structure.
- Do not include Markdown or code fences.
"""

    # First attempt
    raw_response = _generate_response(prompt)

    print("\n----- FINAL INTERVIEW SUMMARY -----")
    print(raw_response)

    try:
        return _parse_summary(raw_response)

    except (json.JSONDecodeError, ValidationError, ValueError):
        logger.warning(
            "Invalid AI summary JSON. Retrying summary generation."
        )

    # Second attempt
    raw_response = _generate_response(prompt, retry=True)

    print("\n----- RETRY INTERVIEW SUMMARY -----")
    print(raw_response)

    try:
        return _parse_summary(raw_response)

    except (json.JSONDecodeError, ValidationError, ValueError):
        logger.exception(
            "AI returned invalid JSON even after retry. Response: %s",
            raw_response,
        )
        raise ValueError(
            "Could not generate a valid interview summary after retry."
        )
