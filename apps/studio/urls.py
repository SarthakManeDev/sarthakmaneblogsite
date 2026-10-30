from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "studio"


def crud(prefix, view_set):
    list_view, create_view, update_view, delete_view = view_set
    return [
        path(f"{prefix}s/", list_view, name=f"{prefix}_list"),
        path(f"{prefix}s/new/", create_view, name=f"{prefix}_create"),
        path(f"{prefix}s/<int:pk>/", update_view, name=f"{prefix}_update"),
        path(f"{prefix}s/<int:pk>/delete/", delete_view, name=f"{prefix}_delete"),
    ]


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="studio/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("books/<int:pk>/progress/", views.book_progress, name="book_progress"),
    path("about/", views.profile, name="profile"),
    path("upload-image/", views.upload_image, name="upload_image"),
    *crud("post", views.post_views),
    *crud("book", views.book_views),
    *crud("headline", views.headline_views),
    *crud("media", views.media_views),
    *crud("exchange", views.exchange_views),
    *crud("photo", views.photo_views),
]
