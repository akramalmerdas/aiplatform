from uuid import uuid4
import markdown

from django.shortcuts import render

# This is a bit of a hack, but it's the simplest way to access the
# in-memory store without introducing a more complex state management system.
from apps.ai.views import _MEMORY, _cid


def _ensure_conv_cookie(resp, request):
    conv_id = request.COOKIES.get("conv_id") or uuid4().hex
    resp.set_cookie(
        "conv_id", conv_id, httponly=True, samesite="Lax", max_age=60 * 60 * 24 * 30
    )
    return resp


def home(request):
    resp = render(request, "index.html")
    return _ensure_conv_cookie(resp, request)


def chat_page(request):
    resp = render(request, "chat.html")
    return _ensure_conv_cookie(resp, request)


def results_page(request):
    conv_id = _cid(request)
    state = _MEMORY.get(conv_id, {})
    plan_md = state.get("last_plan", "")

    # Render markdown to HTML on the server
    plan_html = markdown.markdown(
        plan_md, extensions=['fenced_code', 'tables']
    ) if plan_md else ""

    context = {
        "plan_html": plan_html,
        "plan_md": plan_md,  # Pass raw markdown for download/copy
    }
    resp = render(request, "results.html", context)
    return _ensure_conv_cookie(resp, request)
