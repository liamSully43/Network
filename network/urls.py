
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-post", views.createPost, name="create-post"),
    path("post-like-interaction/<str:post_id>", views.likeInteraction, name="post-like-interaction"),
    path("profile/<str:name>", views.showProfile, name="show-profile"),
    path("following", views.following, name="following"),
    path("followUser/<str:name>", views.followUser, name="followUser"),
    path("unfollowUser/<str:name>", views.unfollowUser, name="unfollowUser"),
    path("updatePost/<str:post_id>", views.updatePost, name="updatePost")
]
