import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from collection.models import Deck, Card
from .models import StudySession, CardProgress
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import json


@login_required
def start_study_session(request, deck_id):
    if "current_card_index" in request.session:
        del request.session["current_card_index"]
    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    study_session = StudySession.objects.create(user=request.user, deck=deck)
    request.session["session_start_time"] = timezone.now().timestamp()
    return redirect("study_session", session_id=study_session.id)


@login_required
def study_session(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    deck = study_session.deck
    if deck.card_set.count() < 4:
        messages.error(
            request, "You need at least 4 cards in this deck to start studying."
        )
        return redirect("home")

    cards = list(Card.objects.filter(deck=study_session.deck))
    current_card_index = request.session.get("current_card_index", 0)
    current_card = cards[current_card_index]

    other_cards = random.sample(cards, 3)
    while current_card in other_cards:
        other_cards = random.sample(cards, 3)
    all_cards = [current_card] + other_cards
    random.shuffle(all_cards)

    context = {
        "study_session": study_session,
        "current_card": current_card,
        "all_cards": all_cards,
        "current_card_number": current_card_index + 1,
        "total_cards": len(cards),
    }
    return render(request, "study_session.html", context)


"""
@login_required
def check_answer(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    cards = list(Card.objects.filter(deck=study_session.deck))
    current_card_index = request.session.get("current_card_index", 0)
    current_card = cards[current_card_index]
    selected_card_id = int(request.POST.get("selected_card"))

    if selected_card_id == current_card.id:
        card_progress, created = CardProgress.objects.get_or_create(
            study_session=study_session, card=current_card
        )
        card_progress.is_correct = True
        card_progress.save()

        if CardProgress.objects.filter(study_session=study_session).count() == len(
            cards
        ):
            # Calculate study duration
            start_time = request.session.get("session_start_time")
            if start_time:
                end_time = timezone.now()
                duration_minutes = (end_time.timestamp() - start_time) / 60

                # Update study session end time
                study_session.ended_at = end_time
                study_session.save()

                # Update profile streak and XP
                profile = request.user.profile
                profile.update_streak(end_time.date(), duration_minutes)
                profile.add_xp(50)  # Add XP for completing the session

                # Clean up session
                if "session_start_time" in request.session:
                    del request.session["session_start_time"]
                if "current_card_index" in request.session:
                    del request.session["current_card_index"]

                messages.success(
                    request,
                    f"Session completed! You earned 50 XP and now have {profile.xp} XP (Level {profile.level})",
                )
                return render(
                    request,
                    "finished.html",
                    {
                        "xp_gained": 50,
                        "total_xp": profile.xp,
                        "level": profile.level,
                        "streak": profile.streak,
                        "study_minutes": round(duration_minutes, 1),
                    },
                )

        current_card_index = (current_card_index + 1) % len(cards)
        request.session["current_card_index"] = current_card_index
        return redirect("study_session", session_id=session_id)
    else:
        messages.error(request, "Incorrect answer. Try again!")
        return redirect("study_session", session_id=session_id)
"""


@login_required
def check_answer(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    cards = list(Card.objects.filter(deck=study_session.deck))
    current_card_index = request.session.get("current_card_index", 0)
    current_card = cards[current_card_index]
    selected_card_id = int(request.POST.get("selected_card"))

    if CardProgress.objects.filter(study_session=study_session).count() == len(cards):
        print(f"DEBUG - Starting session end process")
        print(
            f"DEBUG - Profile study minutes before: {request.user.profile.total_study_minutes}"
        )
        study_session.end_session()
        print(
            f"DEBUG - Profile study minutes after: {request.user.profile.total_study_minutes}"
        )

    if selected_card_id == current_card.id:
        card_progress, created = CardProgress.objects.get_or_create(
            study_session=study_session, card=current_card
        )
        card_progress.is_correct = True
        card_progress.save()

        if CardProgress.objects.filter(study_session=study_session).count() == len(
            cards
        ):
            # End the session using the model method
            study_session.end_session()  # This will handle all profile updates

            profile = request.user.profile
            messages.success(
                request,
                f"Session completed! You earned 50 XP and now have {profile.xp} XP (Level {profile.level})",
            )

            # Clean up session
            if "session_start_time" in request.session:
                del request.session["session_start_time"]
            if "current_card_index" in request.session:
                del request.session["current_card_index"]

            # Calculate duration for template display
            duration_minutes = round(
                (
                    study_session.ended_at.timestamp()
                    - study_session.started_at.timestamp()
                )
                / 60,
                2,
            )

            return render(
                request,
                "finished.html",
                {
                    "xp_gained": 50,
                    "total_xp": profile.xp,
                    "level": profile.level,
                    "streak": profile.streak,
                    "study_minutes": round(duration_minutes, 1),
                    "total_study_minutes": round(profile.total_study_minutes, 2),
                },
            )

        current_card_index = (current_card_index + 1) % len(cards)
        request.session["current_card_index"] = current_card_index
        return redirect("study_session", session_id=session_id)
    else:
        messages.error(request, "Incorrect answer. Try again!")
        return redirect("study_session", session_id=session_id)
