from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm
from collection.models import Deck, Card
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm, PasswordChangeCustomForm
from django.contrib.auth.decorators import login_required
from games.models import Boss, BossProgress


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


@login_required
def home(request):
    # Existing profile and deck logic
    profile = request.user.profile
    decks = Deck.objects.filter(user=request.user)
    total_cards = Card.objects.filter(deck__user=request.user).count()

    # Calculate XP progress to next level
    xp_in_current_level = profile.xp % 100
    xp_progress = xp_in_current_level

    # Get user's active boss progress
    boss_progress = BossProgress.objects.filter(
        user=request.user, boss__is_active=True
    ).first()

    # If user doesn't have an active boss, create one
    if not boss_progress:
        new_boss = Boss.create_random_boss()
        boss_progress = BossProgress.objects.create(
            user=request.user, boss=new_boss, damage_dealt=0
        )

    active_boss = boss_progress.boss

    # Reset boss if it's a new day
    active_boss.reset_boss()

    # Calculate boss health percentage
    boss_health_percent = (active_boss.current_health / active_boss.max_health) * 100

    # Get boss icon based on type
    boss_icons = {
        "CTHULHU": "fa-tentacle",
        "NYARLATHOTEP": "fa-masks-theater",
        "HASTUR": "fa-crown",
        "YOG-SOTHOTH": "fa-eye",
    }
    boss_icon = boss_icons.get(active_boss.boss_type, "fa-dragon")

    # Boss ability information
    boss_abilities = {
        "CTHULHU": {
            "icon": "fa-bolt",
            "name": "XP Drain",
            "description": "Reduces XP gained from study sessions by 50%",
            "effect": "Currently earning only 50% of normal XP",
        },
        "NYARLATHOTEP": {
            "icon": "fa-coins",
            "name": "Gold Rush",
            "description": "Do nothing?",
            "effect": "Do nothing?",
        },
        "HASTUR": {
            "icon": "fa-level-down",
            "name": "Yellow Sign",
            "description": "No Luck",
            "effect": "Reduce XP gained each sessions in range of 10-90%",
        },
        "YOG-SOTHOTH": {
            "icon": "fa-mask",
            "name": "Identity Theft",
            "description": "Temporarily remove your username",
            "effect": "Remove your username",
        },
    }

    boss_ability = boss_abilities.get(
        active_boss.boss_type,
        {
            "icon": "fa-question",
            "name": "Unknown Ability",
            "description": "This boss's powers are mysterious",
            "effect": None,
        },
    )

    context = {
        "profile": profile,
        "decks": decks,
        "total_cards": total_cards,
        "xp_progress": xp_progress,
        "active_boss": active_boss,
        "boss_progress": boss_progress,
        "boss_health_percent": boss_health_percent,
        "boss_icon": boss_icon,
        "boss_ability_icon": boss_ability["icon"],
        "boss_ability_name": boss_ability["name"],
        "boss_ability_description": boss_ability["description"],
        "boss_ability_effect": boss_ability["effect"],
    }

    return render(request, "home.html", context)


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
