from django.urls import path

from . import views

urlpatterns = [
    path("api/message", views.api_message, name="api_message"),
    path("api/last-plan", views.api_last_plan, name="api_last_plan"),
    path("api/health", views.api_health, name="api_health"),
]
