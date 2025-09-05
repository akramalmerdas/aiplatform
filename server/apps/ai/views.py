# server/apps/ai/views.py
import inspect
import json
import logging
from typing import Any, Dict, Tuple

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.ai.services import agent_core, interviewer, research
from apps.ai.services.agent_core import generate_markdown_plan
from apps.ai.services.interviewer import next_turn_guided

log = logging.getLogger(__name__)


# research may be in research.py or researcher.py (support both)
try:
    from apps.ai.services.research import research_market
except Exception:
    try:
        from apps.ai.services.researcher import research_market  # type: ignore
    except Exception as e:
        research_market = None  # runtime check below
        log.warning(
            "Could not import research_market from research or researcher: %s", e
        )

# ---- Simple per-process memory store (OK for dev) ----
_MEMORY: Dict[str, Any] = {}

QUESTION_FALLBACK = "Thanks. Tell me about your target customer next."


def _cid(request) -> str:
    return request.COOKIES.get("conv_id") or "anon"


def _store(conv_id: str) -> Dict[str, Any]:
    s = _MEMORY.setdefault(
        conv_id,
        {
            "state": "INTAKE",
            "answers": {},
            "history": [{"role": "system", "content": "(guided interviewer active)"}],
            "template": "template_a_ministry",
            "last_plan": "",
        },
    )
    return s


def _merge_answers(dst: Dict[str, str], updates: Dict[str, str]) -> None:
    if not updates:
        return
    for k, v in updates.items():
        if v is None:
            continue
        dst[k] = (v or "").strip()


def _ok(
    bot: str,
    done: bool = False,
    results_url: str | None = None,
    extra: Dict[str, Any] | None = None,
):
    payload = {"bot": bot, "done": done}
    if results_url:
        payload["results_url"] = results_url
    if extra:
        payload.update(extra)
    return JsonResponse(payload)


@csrf_exempt  # for dev; switch to CSRF token later
def api_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    conv = _cid(request)
    state = _store(conv)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    user_text = (data.get("message") or "").strip()
    lang = getattr(settings, "LANG", "English")

    answers: Dict[str, str] = state["answers"]
    history: list[Dict[str, str]] = state["history"]

    # If interview already completed
    if state.get("state") == "COMPLETE":
        return _ok(
            "Interview completed. Open the Results page.",
            done=True,
            results_url="/results",
        )

    # Kickoff (first turn): ask first question
    if len(history) == 1 and user_text == "":
        try:
            updates, next_q, _done = _safe_next_turn(answers, "", lang)
            _merge_answers(answers, updates)
            history.append({"role": "assistant", "content": next_q})
            return _ok(next_q, done=False)
        except Exception as e:
            log.exception("kickoff failed: %s", e)
            return _ok("What is your company name?", done=False)

    # Results trigger
    if user_text.upper() == "RESULTS":
        if research_market is None:
            msg = "Research module not found. Is research.py present?"
            return JsonResponse({"bot": msg, "done": False}, status=500)
        try:
            # final sync turn to capture any last updates
            _merge_answers(answers, {})
            # run research + plan
            research = research_market(answers)
            template_id = state.get("template", "template_a_ministry")
            plan_md, _preview = generate_markdown_plan(
                answers=answers,
                research=research,
                template_id=template_id,
                language=lang,
            )
            state["last_plan"] = plan_md
            state["state"] = "COMPLETE"
            return _ok(
                "Done. Your plan is ready—open the Results page.",
                done=True,
                results_url="/results",
            )
        except Exception as e:
            log.exception("plan generation failed: %s", e)
            return JsonResponse(
                {"bot": "Sorry—failed to generate the plan.", "error": str(e)},
                status=500,
            )

    # Normal interview turn
    if user_text:
        history.append({"role": "user", "content": user_text})

    try:
        updates, next_q, _done = _safe_next_turn(answers, user_text, lang)
        _merge_answers(answers, updates)
        if not next_q or (
            history
            and history[-1]["role"] == "assistant"
            and history[-1]["content"].strip() == next_q.strip()
        ):
            # Avoid echo/loop; give a sensible fallback
            next_q = QUESTION_FALLBACK
        history.append({"role": "assistant", "content": next_q})
        return _ok(next_q, done=False)
    except Exception as e:
        log.exception("turn failed: %s", e)
        fallback = "Thanks. Who is on your core team and what are their roles?"
        history.append({"role": "assistant", "content": fallback})
        return _ok(fallback, done=False)


def _safe_next_turn(
    answers: Dict[str, str], user_text: str, lang: str
) -> Tuple[Dict[str, str], str, bool]:
    """
    Wrapper over next_turn_guided that guards against None returns.
    Expected signature: (updates: dict, next_q: str, done: bool)
    """
    updates, next_q, done = next_turn_guided(answers, user_text, language=lang)
    if updates is None:
        updates = {}
    next_q = (next_q or "").strip() or "Thanks. Next detail?"
    return updates, next_q, bool(done)


def api_last_plan(request):
    conv = _cid(request)
    state = _store(conv)
    return JsonResponse({"plan": state.get("last_plan", "")})


def api_health(request):
    return JsonResponse(
        {
            "status": "ok",
            "modules": {
                "interviewer": inspect.getfile(interviewer),
                "agent_core": inspect.getfile(agent_core),
                "research": inspect.getfile(research),
            },
        }
    )
