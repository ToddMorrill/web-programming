
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("user/<int:user_id>", views.user, name="user"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit-post", views.edit_post, name="edit-post"),
    path("like", views.like, name="like")
]
