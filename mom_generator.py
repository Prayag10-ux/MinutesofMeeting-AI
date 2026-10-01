import json
import os
import re

import ollama
from openai import OpenAI


LOCAL_MODEL = "gemma3:4b"

# Groq's OpenAI-compatible API
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def clean_json_response(response_text):
    response_text = response_text.strip()

    response_text = re.sub(
        r"^```json\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    response_text = re.sub(
        r"^```\s*",
        "",
        response_text
    )

    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )

    response_text = response_text.strip()

    start = response_text.find("{")
    end = response_text.rfind("}")

    if start != -1 and end != -1:
        response_text = response_text[start:end + 1]

    return response_text


def validate_mom(data):

    if not isinstance(data, dict):
        data = {}

    agenda = data.get("agenda", "Not specified")

    if not isinstance(agenda, str):
        agenda = "Not specified"

    discussion_points = data.get("discussion_points", [])

    if not isinstance(discussion_points, list):
        discussion_points = []

    discussion_points = [
        str(point).strip()
        for point in discussion_points
        if str(point).strip()
    ]

    decisions = data.get("decisions", [])

    if not isinstance(decisions, list):
        decisions = []

    decisions = [
        str(decision).strip()
        for decision in decisions
        if str(decision).strip()
    ]

    action_items = data.get("action_items", [])

    if not isinstance(action_items, list):
        action_items = []

    cleaned_actions = []

    for action in action_items:

        if not isinstance(action, dict):
            continue

        responsible = action.get(
            "responsible",
            "Not specified"
        )

        task = action.get(
            "task",
            "Not specified"
        )

        if not isinstance(responsible, str):
            responsible = "Not specified"

        if not isinstance(task, str):
            task = "Not specified"

        responsible = responsible.strip()
        task = task.strip()

        if not responsible:
            responsible = "Not specified"

        if not task:
            task = "Not specified"

        cleaned_actions.append(
            {
                "responsible": responsible,
                "task": task
            }
        )

    # Remove duplicate discussion points
    discussion_points = list(
        dict.fromkeys(discussion_points)
    )

    # Remove duplicate decisions
    decisions = list(
        dict.fromkeys(decisions)
    )

    # Remove duplicate action items
    unique_actions = []
    seen_actions = set()

    for action in cleaned_actions:

        key = (
            action["responsible"].lower(),
            action["task"].lower()
        )

        if key in seen_actions:
            continue

        seen_actions.add(key)
        unique_actions.append(action)

    return {
        "agenda": agenda,
        "discussion_points": discussion_points,
        "decisions": decisions,
        "action_items": unique_actions
    }


SYSTEM_PROMPT = """
You are an AI assistant that converts meeting transcripts into
professional Minutes of Meeting.

Use ONLY information present in the transcript.

Do not invent names, decisions, responsibilities, dates, deadlines,
or facts that are not present.

Return ONLY valid JSON.

Use exactly this structure:

{
    "agenda": "string",
    "discussion_points": [
        "string"
    ],
    "decisions": [
        "string"
    ],
    "action_items": [
        {
            "responsible": "string",
            "task": "string"
        }
    ]
}

Rules:

1. agenda:
   Summarize the main purpose or agenda of the meeting.

2. discussion_points:
   Extract important topics actually discussed.

3. decisions:
   Extract decisions that were actually made.
   Do not treat suggestions as decisions.

4. action_items:
   Extract tasks that participants agreed to perform.

5. responsible:
   Include the responsible person only if the transcript
   clearly identifies them.

6. Never invent missing information.

7. If something is not available, use:
   "Not specified"

8. Keep the output concise and professional.
"""


def build_user_prompt(transcript, participants):

    participant_text = participants.strip()

    if not participant_text:
        participant_text = "Not specified"

    return f"""
Participants provided by the user:
{participant_text}

Meeting transcript:
{transcript}

Generate the Minutes of Meeting from this transcript.

Remember:
- Do not invent information.
- Use only the transcript.
- Return valid JSON only.
"""


def generate_with_ollama(transcript, participants):

    response = ollama.chat(
        model=LOCAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": build_user_prompt(
                    transcript,
                    participants
                )
            }
        ],
        options={
            "temperature": 0.1
        }
    )

    return response["message"]["content"]


def generate_with_groq(transcript, participants):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": build_user_prompt(
                    transcript,
                    participants
                )
            }
        ]
    )

    return response.choices[0].message.content


def generate_mom(transcript, participants=""):

    if not transcript or not transcript.strip():

        return {
            "agenda": "Not specified",
            "discussion_points": [],
            "decisions": [],
            "action_items": []
        }

    groq_api_key = os.getenv("GROQ_API_KEY")

    try:

        # Cloud deployment:
        # Railway has GROQ_API_KEY configured.
        if groq_api_key:

            raw_response = generate_with_groq(
                transcript,
                participants
            )

        # Local development:
        # No Groq key means use Ollama + Gemma.
        else:

            raw_response = generate_with_ollama(
                transcript,
                participants
            )

        json_text = clean_json_response(
            raw_response
        )

        mom = json.loads(json_text)

        return validate_mom(mom)

    except json.JSONDecodeError as e:

        raise RuntimeError(
            f"AI returned invalid JSON: {e}"
        )

    except Exception as e:

        raise RuntimeError(
            f"AI could not generate the MoM: {e}"
        )
