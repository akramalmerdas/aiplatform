# interviewer.py
import json
from typing import Any, Dict, Tuple

# The guided order we want to cover — internal/team only
INTERVIEW_FLOW = [
    "idea_summary",
    "solution",
    "value_prop",
    "target_customer",
    "differentiation",
    "business_model",
    "team",
    "execution_plan",
    "goals_90d",
    "risks",
]

FIELD_LABELS = {
    "idea_summary": "your overall idea (1–2 sentences)",
    "solution": "your solution (what you provide)",
    "value_prop": "why it’s unique / valuable",
    "target_customer": "your ideal customer in Spain",
    "differentiation": "how you differ from alternatives",
    "business_model": "how you’ll make money (subscription, consulting, etc.)",
    "team": "your team and their roles",
    "execution_plan": "your plan to start operations (high level)",
    "goals_90d": "your top 2–3 goals for the first 90 days",
    "risks": "the main risks and your mitigations",
}

SYSTEM_GUIDED = """You are an interviewer helping an entrepreneur describe their idea.
Ask ONE concise question at a time about the NEXT MISSING FIELD ONLY from the given
flow.
Do NOT ask for competitors, market size, regulations, or pricing benchmarks (those
are researched later).
Keep it professional and brief. When all fields are covered, say:
'OK, type RESULTS to see the plan.'
"""


def _safe_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return {}


def _first_missing(answers: Dict[str, Any]) -> str:
    for f in INTERVIEW_FLOW:
        if not (answers.get(f) or "").strip():
            return f
    return ""


def _should_skip(text: str) -> bool:
    t = (text or "").lower()
    return any(
        p in t
        for p in [
            "i already told",
            "i just told",
            "as i said",
            "i said",
            "told you",
            "already said",
        ]
    )


def next_turn_guided(
    answers: Dict[str, Any], last_user: str, language="English"
) -> Tuple[Dict[str, str], str, bool]:
    """
    Deterministic progression:
    - Find next missing field
    - If user provided content, capture it into that field (unless they say they
      already answered)
    - Move on to the next field with a fresh question
    - LLM is used only as a helper; we never depend on it to progress
    """
    # 1) Which field are we on?
    current_field = _first_missing(answers)
    if not current_field:
        return {}, "OK, type RESULTS to see the plan.", False

    user_text = (last_user or "").strip()

    # 2) Capture the user's message into the current field if it looks like content
    updates: Dict[str, str] = {}
    if user_text and not _should_skip(user_text):
        # If very short / not informative, we won't capture
        # (keeps quality a bit higher)
        if len(user_text) >= 10:
            updates[current_field] = user_text

    # 3) Optionally ask LLM to refine the question — but we won't block on it
    next_field_after = current_field
    if updates.get(current_field):
        # pretend we've filled it to compute the next slot
        tmp = answers.copy()
        tmp.update(updates)
        next_field_after = _first_missing(tmp)

    if not next_field_after:
        # everything covered now
        return updates, "OK, type RESULTS to see the plan.", True

    # Deterministic fallback question
    next_q = f"Thanks. Now tell me about {FIELD_LABELS[next_field_after]}."

    return updates, next_q, False
