from django.urls import path

from . import views

urlpatterns = [
path("loginprompt/", views.loginprompt, name="loginprompt"),
]