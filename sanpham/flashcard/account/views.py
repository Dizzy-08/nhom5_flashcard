from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm
from collection.models import Deck, Card
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm, PasswordChangeCustomForm
from django.contrib.auth.decorators import login_required
import calendar
from datetime import datetime, timedelta
import json
from study.models import StudySession
from games.models import Boss, BossProgress, UserItem


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


"""
def home(request):
    if request.user.is_authenticated:
        decks = Deck.objects.filter(user=request.user)
        profile = request.user.profile
        today = datetime.now().date()
        year_ago = today - timedelta(days=365)

        study_sessions = StudySession.objects.filter(
            user=request.user,
            started_at__gte=year_ago,
            ended_at__isnull=False,  # Only count completed sessions
        ).values_list("started_at", flat=True)

        # Create a dictionary of study days
        study_data = {}
        for session_datetime in study_sessions:
            # Convert to date string in YYYY-MM-DD format
            date_str = session_datetime.strftime("%Y-%m-%d")
            study_data[date_str] = True

        total_cards = sum(deck.card_set.count() for deck in decks)

        active_boss = Boss.objects.filter(is_active=True).first()
        if not active_boss:
            # Create a default boss if none exists
            active_boss = Boss.objects.create(
                name="Tutorial Boss",
                boss_type="CTHULHU",
                description="A training boss to help you learn the game mechanics.",
                max_health=1000,
                current_health=1000,
                damage_per_study=500,
            )

        # Reset boss if it's a new day
        active_boss.reset_boss()

        # Get or create boss progress
        boss_progress, created = BossProgress.objects.get_or_create(
            user=request.user, boss=active_boss
        )

        # Calculate boss health percentage
        boss_health_percent = (
            active_boss.current_health / active_boss.max_health
        ) * 100

        # Get boss icon based on type
        boss_icons = {
            "CTHULHU": "fa-skull",
            "NYARLATHOTEP": "fa-sack-dollar",
            "HASTUR": "fa-level-down-alt",
            "YOG-SOTHOTH": "fa-user-secret",
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
                "description": "Steals all coins at the end of the day",
                "effect": "Will steal all coins when day ends",
            },
            "HASTUR": {
                "icon": "fa-level-down",
                "name": "Level Curse",
                "description": "Decreases your level by 1 at the end of the day",
                "effect": "Will reduce level by 1 when day ends",
            },
            "YOG-SOTHOTH": {
                "icon": "fa-mask",
                "name": "Identity Theft",
                "description": "Temporarily changes your username",
                "effect": "Will change username to john_doe_X",
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

        # Get active items
        active_items = UserItem.objects.filter(
            user=request.user, is_active=True
        ).select_related("item")

        context = {
            "decks": decks,
            "profile": profile,
            "xp_to_next_level": 100 - (profile.xp % 100),  # XP needed for next level
            "xp_progress": (profile.xp % 100),  # Progress within current level
            "study_data": json.dumps(study_data),
            "total_cards": total_cards,
            "active_boss": active_boss,
            "boss_progress": boss_progress,
            "boss_health_percent": boss_health_percent,
            "boss_icon": boss_icon,
            "boss_ability_icon": boss_ability["icon"],
            "boss_ability_name": boss_ability["name"],
            "boss_ability_description": boss_ability["description"],
            "boss_ability_effect": boss_ability["effect"],
            "active_items": active_items,
        }
        return render(request, "home.html", context)
    else:
        return redirect("login")
"""


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
            "description": "Steals all coins at the end of the day",
            "effect": "Will steal all coins when day ends",
        },
        "HASTUR": {
            "icon": "fa-level-down",
            "name": "Level Curse",
            "description": "Decreases your level by 1 at the end of the day",
            "effect": "Will reduce level by 1 when day ends",
        },
        "YOG-SOTHOTH": {
            "icon": "fa-mask",
            "name": "Identity Theft",
            "description": "Temporarily changes your username",
            "effect": "Will change username to john_doe_X",
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

    # Get active items
    active_items = UserItem.objects.filter(
        user=request.user, is_active=True
    ).select_related("item")

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
        "active_items": active_items,
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
