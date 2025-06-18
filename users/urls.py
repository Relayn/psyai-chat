from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import HomePageView, SignUpView, profile_view

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
]
