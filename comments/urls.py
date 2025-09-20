from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("leave/", views.leave_comment, name="leave_comment"),
    path("all/", views.all_comments, name="all_comments"),
]
