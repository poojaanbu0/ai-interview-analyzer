import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)


class FinalInterviewSummary(BaseModel):
    overall_summary: str
    key_strengths: list[str]
    improvement_areas: list[str]
    technical_topics: list[str]
    communication_observations: list[str]


def generate_interview_summary(
    interview_history: list
) -> FinalInterviewSummary:

    # Convert all interview rounds into readable text
    interview_text = ""

    for index, round_data in enumerate(
        interview_history,
        start=1
    ):

        interview_text += f"""
Interview Round {index}

Question:
{round_data["question"]}

Candidate Answer:
{round_data["transcript"]}

Answer Analysis:
{json.dumps(round_data["answer_analysis"])}

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

Return ONLY valid JSON with exactly this structure:

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
- Return valid JSON only.
- Do not use Markdown.
- Do not use code fences.
- Keep JSON string values on one line.
"""


    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an interview summary assistant. "
                    "Summarize evidence from the completed interview. "
                    "Return only valid JSON."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        max_tokens=700,

        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    )


    raw_response = (
        response.choices[0].message.content
    )


    print("\n----- FINAL INTERVIEW SUMMARY -----")
    print(raw_response)


    parsed_json = json.loads(
        raw_response,
        strict=False
    )


    validated_summary = FinalInterviewSummary(
        **parsed_json
    )


    return validated_summary