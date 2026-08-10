from django.urls import path
from .views import LoginPageView, RegisterPageView, login_view, register_view, home_view, HomePageView

urlpatterns = [
    path("", login_view, name="login"),
    path("login/", login_view, name="login_page"),
    path("register/", register_view, name="register"),
    path("home/", home_view, name="home"),
]