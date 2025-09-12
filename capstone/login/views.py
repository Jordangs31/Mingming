from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.generic import TemplateView

class LoginPageView(TemplateView):
    template_name = "app/login.html"

class RegisterPageView(TemplateView):
    template_name = "app/register.html"

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # change "home" to your homepage url name
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login/login.html")