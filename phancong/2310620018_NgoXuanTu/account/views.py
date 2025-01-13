from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm
from collection.models import Deck


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # immediately login if signup success
            return redirect("home")
    else:
        form = SignupForm
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")

    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def home(request):
    if request.user.is_authenticated:
        decks = Deck.objects.filter(user=request.user)
        profile = request.user.profile

        context = {
            "decks": decks,
            "profile": profile,
            "xp_to_next_level": 100 - (profile.xp % 100),  # XP needed for next level
            "xp_progress": (profile.xp % 100),  # Progress within current level
        }
        return render(request, "home.html", context)
    else:
        return redirect("login")
