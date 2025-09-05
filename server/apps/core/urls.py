from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("chat", views.chat_page, name="chat"),
    path("results", views.results_page, name="results"),
]
