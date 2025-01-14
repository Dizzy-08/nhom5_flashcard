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


@login_required
def check_answer(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    cards = list(Card.objects.filter(deck=study_session.deck))
    current_card_index = request.session.get("current_card_index", 0)
    current_card = cards[current_card_index]

    # Get the selected card
    selected_card_id = int(request.POST.get("selected_card"))

    if selected_card_id == current_card.id:
        # Record correct answer
        card_progress, created = CardProgress.objects.get_or_create(
            study_session=study_session, card=current_card
        )
        card_progress.is_correct = True
        card_progress.save()

        # Check if session is complete
        if CardProgress.objects.filter(study_session=study_session).count() == len(
            cards
        ):
            # End the session and get XP gained
            xp_gained = study_session.end_session()
            profile = request.user.profile

            # Clean up session
            request.session.pop("session_start_time", None)
            request.session.pop("current_card_index", None)

            # Calculate duration
            duration_minutes = round(
                (study_session.ended_at - study_session.started_at).total_seconds()
                / 60,
                2,
            )

            # Show completion message
            messages.success(
                request,
                f"Session completed! You earned {xp_gained} XP and now have {profile.xp} XP (Level {profile.level})",
            )
            print(f"XP gained {xp_gained}")

            return render(
                request,
                "finished.html",
                {
                    "xp_gained": xp_gained,
                    "total_xp": profile.xp,
                    "level": profile.level,
                    "streak": profile.streak,
                    "study_minutes": duration_minutes,
                    "total_study_minutes": profile.total_study_minutes,
                },
            )

        # Move to next card
        current_card_index = (current_card_index + 1) % len(cards)
        request.session["current_card_index"] = current_card_index
        return redirect("study_session", session_id=session_id)

    else:
        messages.error(request, "Incorrect answer. Try again!")
        return redirect("study_session", session_id=session_id)
