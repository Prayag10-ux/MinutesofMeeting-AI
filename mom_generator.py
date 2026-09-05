import json
import re
import ollama


# ============================================================
# GEMMA MODEL
# ============================================================

MODEL_NAME = "gemma3:4b"


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json_response(response_text):
    """
    Gemma may sometimes wrap JSON inside markdown code blocks.
    This function extracts the JSON safely.
    """

    response_text = response_text.strip()

    # Remove markdown code fences
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

    # Find the first JSON object if Gemma added extra text
    start = response_text.find("{")
    end = response_text.rfind("}")

    if start != -1 and end != -1:
        response_text = response_text[start:end + 1]

    return response_text


# ============================================================
# VALIDATE MOM
# ============================================================

def validate_mom(data):
    """
    Makes sure the output has the structure expected
    by the rest of the application.
    """

    if not isinstance(data, dict):
        data = {}

    # --------------------------------------------------------
    # Agenda
    # --------------------------------------------------------

    agenda = data.get(
        "agenda",
        "Not specified"
    )

    if not isinstance(agenda, str):
        agenda = "Not specified"

    # --------------------------------------------------------
    # Discussion Points
    # --------------------------------------------------------

    discussion_points = data.get(
        "discussion_points",
        []
    )

    if not isinstance(discussion_points, list):
        discussion_points = []

    discussion_points = [
        str(point).strip()
        for point in discussion_points
        if str(point).strip()
    ]

    # --------------------------------------------------------
    # Decisions
    # --------------------------------------------------------

    decisions = data.get(
        "decisions",
        []
    )

    if not isinstance(decisions, list):
        decisions = []

    decisions = [
        str(decision).strip()
        for decision in decisions
        if str(decision).strip()
    ]

    # --------------------------------------------------------
    # Action Items
    # --------------------------------------------------------

    action_items = data.get(
        "action_items",
        []
    )

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

    # --------------------------------------------------------
    # Remove duplicate discussion points
    # --------------------------------------------------------

    discussion_points = list(
        dict.fromkeys(discussion_points)
    )

    # --------------------------------------------------------
    # Remove duplicate decisions
    # --------------------------------------------------------

    decisions = list(
        dict.fromkeys(decisions)
    )

    # --------------------------------------------------------
    # Remove duplicate actions
    # --------------------------------------------------------

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


# ============================================================
# MAIN MOM GENERATOR
# ============================================================

def generate_mom(
    transcript,
    participants=""
):
    """
    Uses Gemma 3 4B to convert a meeting transcript
    into structured Minutes of Meeting.
    """

    if not transcript or not transcript.strip():

        return {
            "agenda": "Not specified",
            "discussion_points": [],
            "decisions": [],
            "action_items": []
        }

    # ========================================================
    # SYSTEM INSTRUCTION
    # ========================================================

    system_prompt = """
You are an expert Minutes of Meeting (MoM) assistant.

Your job is to carefully analyse a meeting transcript and
convert it into a clean, professional and concise Minutes
of Meeting.

You MUST follow these rules:

1. Use ONLY information explicitly present in the transcript.
2. DO NOT invent facts.
3. DO NOT add information that was not discussed.
4. Do not include greetings such as "Good morning".
5. Do not include "thank you", "okay", "sure", or other
   meaningless conversational responses.
6. Do not put questions into Decisions.
7. Do not put general discussion into Action Items.
8. Identify actual decisions separately from discussion.
9. Identify clear tasks and the person responsible for them.
10. If a task is clearly assigned to a person, use that person's
    name as the responsible person.
11. If a person says "I'll..." immediately after another speaker
    assigns them a task, associate the task with that person.
12. Keep discussion points concise. Combine closely related
    statements into one useful point.
13. Keep decisions concise and specific.
14. Keep action items concise and specific.
15. Do not repeat the same information in multiple sections
    unless necessary.
16. If something is not present in the transcript, return
    "Not specified" for the agenda and an empty list for
    sections where there is no information.
17. Return ONLY valid JSON.
18. Do NOT use markdown.
19. Do NOT explain your reasoning.
20. Do NOT include anything before or after the JSON.

The JSON MUST have exactly this structure:

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
"""


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""
Known participants:

{participants if participants else "Not specified"}

Meeting transcript:

{transcript}

Now generate the Minutes of Meeting.

Pay special attention to:

- What the meeting is about
- Main topics discussed
- Actual decisions
- Tasks assigned to participants
- Who is responsible for each task
- Any follow-up meeting that was actually agreed upon

Return ONLY the required JSON.
"""


    # ========================================================
    # CALL GEMMA
    # ========================================================

    try:

        response = ollama.chat(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            options={
                "temperature": 0.1
            }
        )


        # ====================================================
        # GET RESPONSE
        # ====================================================

        raw_response = response["message"]["content"]

        # ====================================================
        # CLEAN RESPONSE
        # ====================================================

        json_text = clean_json_response(
            raw_response
        )

        # ====================================================
        # PARSE JSON
        # ====================================================

        mom = json.loads(
            json_text
        )

        # ====================================================
        # VALIDATE
        # ====================================================

        return validate_mom(
            mom
        )

    except json.JSONDecodeError:

        # If Gemma somehow returns invalid JSON,
        # return a safe empty structure instead of crashing.

        return {
            "agenda": "Not specified",
            "discussion_points": [],
            "decisions": [],
            "action_items": []
        }

    except Exception as e:

        # Display the actual error in Streamlit
        # so debugging is easier.

        raise RuntimeError(
            f"Gemma could not generate the MoM: {e}"
        )