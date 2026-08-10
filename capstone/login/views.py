from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = "app/home.html"

class LoginPageView(TemplateView):
    template_name = "app/login.html"

class RegisterPageView(TemplateView):
    template_name = "app/register.html"


def home_view(request):
    return render(request, "app/home.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")

        messages.error(request, "Invalid username or password")

    return render(request, "app/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            messages.error(request, "Please complete all fields.")
            return render(request, "app/register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "app/register.html")

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken.")
            return render(request, "app/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "That email is already registered.")
            return render(request, "app/register.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        user.save()

        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("login")

    return render(request, "app/register.html")