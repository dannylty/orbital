from django.urls import path

from . import views

urlpatterns = [
path("", views.view, name="view"),
path("home", views.view, name="view"),
path("view", views.view, name="view"),
path("create", views.create, name="create"),
path("profile/<int:id>", views.profile, name="profile"),
path("edit_profile", views.editprofile, name="editprofile"),
path("thread/<int:id>", views.index, name="index"),
path("threadchat/<int:id>", views.threadchat, name="threadchat"),
path("notifications", views.notifications, name="notifications"),
path("chatlist", views.chatlist, name="chatlist"),
path("search", views.search, name="search"),
path("thread/<int:id>/edit", views.editthread, name="editthread"),
path("thread/<int:id>/delete", views.deletethread, name="deletethread"),
path("edit_profile_thread", views.editprofilethread, name="editprofilethread"),
]
