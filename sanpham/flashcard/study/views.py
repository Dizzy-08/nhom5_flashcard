import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from collection.models import Deck, Card
from .models import StudySession, CardProgress
from django.contrib import messages
from django.utils import timezone


@login_required
def start_study_session(request, deck_id):
    # Clear any existing session data
    for key in ["current_card_index", "shuffled_card_ids"]:
        if key in request.session:
            del request.session[key]

    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    study_session = StudySession.objects.create(user=request.user, deck=deck)

    # Get all card IDs and shuffle them
    card_ids = list(Card.objects.filter(deck=deck).values_list("id", flat=True))
    random.shuffle(card_ids)

    # Store shuffled card IDs in session
    request.session["shuffled_card_ids"] = card_ids
    request.session["session_start_time"] = timezone.now().timestamp()

    return redirect("study_session", session_id=study_session.id)


@login_required
def study_session(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    deck = study_session.deck

    # Get shuffled card IDs from session
    shuffled_card_ids = request.session.get("shuffled_card_ids")
    if not shuffled_card_ids:
        # If somehow lost, recreate shuffled order
        shuffled_card_ids = list(
            Card.objects.filter(deck=deck).values_list("id", flat=True)
        )
        random.shuffle(shuffled_card_ids)
        request.session["shuffled_card_ids"] = shuffled_card_ids

    if len(shuffled_card_ids) < 4:
        messages.error(
            request, "You need at least 4 cards in this deck to start studying."
        )
        return redirect("home")

    current_card_index = request.session.get("current_card_index", 0)
    current_card = get_object_or_404(Card, pk=shuffled_card_ids[current_card_index])

    # Get other random cards for multiple choice, excluding current card
    other_card_ids = [id for id in shuffled_card_ids if id != current_card.id]
    other_cards = list(Card.objects.filter(pk__in=random.sample(other_card_ids, 3)))

    # Combine and shuffle all options
    all_cards = [current_card] + other_cards
    random.shuffle(all_cards)

    context = {
        "study_session": study_session,
        "current_card": current_card,
        "all_cards": all_cards,
        "current_card_number": current_card_index + 1,
        "total_cards": len(shuffled_card_ids),
    }
    return render(request, "study_session.html", context)


@login_required
def check_answer(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    shuffled_card_ids = request.session.get("shuffled_card_ids", [])
    current_card_index = request.session.get("current_card_index", 0)

    current_card = get_object_or_404(Card, pk=shuffled_card_ids[current_card_index])
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
            shuffled_card_ids
        ):
            # End session and calculate XP
            xp_gained = study_session.end_session()
            profile = request.user.profile

            # Clean up session
            for key in [
                "session_start_time",
                "current_card_index",
                "shuffled_card_ids",
            ]:
                request.session.pop(key, None)

            # Calculate duration
            duration_minutes = round(
                (study_session.ended_at - study_session.started_at).total_seconds()
                / 60,
                2,
            )

            messages.success(
                request,
                f"Session completed! You earned {xp_gained} XP and now have {profile.xp} XP (Level {profile.level})",
            )

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
        current_card_index = (current_card_index + 1) % len(shuffled_card_ids)
        request.session["current_card_index"] = current_card_index
        return redirect("study_session", session_id=session_id)
    else:
        messages.error(request, "Incorrect answer. Try again!")
        return redirect("study_session", session_id=session_id)
