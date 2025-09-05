from uuid import uuid4
from django.shortcuts import render

def _ensure_conv_cookie(resp, request):
    conv_id = request.COOKIES.get("conv_id") or uuid4().hex
    resp.set_cookie("conv_id", conv_id, httponly=True, samesite="Lax", max_age=60*60*24*30)
    return resp

def home(request):
    resp = render(request, "index.html")
    return _ensure_conv_cookie(resp, request)

def chat_page(request):
    resp = render(request, "chat.html")
    return _ensure_conv_cookie(resp, request)

def results_page(request):
    resp = render(request, "results.html")
    return _ensure_conv_cookie(resp, request)
