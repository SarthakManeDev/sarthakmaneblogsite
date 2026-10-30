from django.urls import path

from . import views

app_name = "tea"
urlpatterns = [
    path("", views.exchange_list, name="list"),
    path("<slug:slug>/", views.exchange_detail, name="detail"),
]
