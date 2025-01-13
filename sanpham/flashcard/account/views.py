from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm
from collection.models import Deck
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm, PasswordChangeCustomForm
from django.contrib.auth.decorators import login_required


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
                pass
        else:
            pass

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


@login_required
def edit_profile(request):
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("home")
    else:
        user_form = UserEditForm(instance=request.user)

    return render(
        request,
        "edit_profile.html",
        {
            "user_form": user_form,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeCustomForm(request.POST)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data["old_password"]):
                request.user.set_password(form.cleaned_data["new_password1"])
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
                messages.success(request, "Your password was successfully updated!")
                return redirect("home")
            else:
                messages.error(request, "Current password is incorrect.")
    else:
        form = PasswordChangeCustomForm()

    return render(request, "change_password.html", {"form": form})
