from django.urls import path

from . import views

urlpatterns = [
path("<int:id>", views.index, name="index"),
path("", views.home, name="home"),
path("home", views.view, name="view"),
path("create", views.create, name="create"),
path("view", views.view, name="view"),
path("profile", views.profile, name="profile"),
path("edit_profile", views.editprofile, name="editprofile"),
path("thread/<int:id>", views.index, name="index"),
path("threadchat/<int:id>", views.threadchat, name="threadchat"),
path("notifications", views.notifications, name="notifications"),
]