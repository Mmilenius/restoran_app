from django.contrib import admin
from django.urls import path
from allauth.account import views as allauth_views
from users import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path("profile/", views.profile, name="profile"),
    path('email-sent/', views.EmailConfirmationSentView.as_view(), name='email_sent'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)