from django.urls import path

from . import views

urlpatterns = [
# not required anymore?
# path("<int:id>", views.index, name="index"),
path("", views.view, name="view"),
path("home", views.view, name="view"),
path("view", views.view, name="view"),
path("create", views.create, name="create"),
path("profile", views.profile, name="profile"),
path("edit_profile", views.editprofile, name="editprofile"),
path("thread/<int:id>", views.index, name="index"),
path("threadchat/<int:id>", views.threadchat, name="threadchat"),
path("notifications", views.notifications, name="notifications"),
]
