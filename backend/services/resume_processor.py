
"""Resume text extraction and candidate summary generation."""

import os

import fitz  # PyMuPDF
import docx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None


def _get_nvidia_client():
    global _client
    if _client is None:
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise RuntimeError("NVIDIA_API_KEY is missing from environment variables")
        _client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
        )
    return _client


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from a PDF or DOCX file."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text

    if ext in ("docx",):
        import io
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError(f"Unsupported file type: .{ext}")


def generate_candidate_summary(resume_text: str, job_description: str) -> str:
    """Generate a concise summary of the candidate relative to the JD."""
    client = _get_nvidia_client()

    prompt = f"""You are an HR assistant. Given a candidate's resume and a job description,
provide a concise summary of the candidate's qualifications relative to the job.
Highlight relevant experience, skills matches, and any gaps.

Job Description:
{job_description}

Resume:
{resume_text}

Provide a concise summary (3-5 paragraphs)."""

    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    return response.choices[0].message.content.strip()
