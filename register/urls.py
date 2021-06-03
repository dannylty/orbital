from django.urls import path

from . import views

urlpatterns = [
path("loginprompt/", views.loginprompt, name="loginprompt"),
path("log-out/", views.logout, name="logout"),
]