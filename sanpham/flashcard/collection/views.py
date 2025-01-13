from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Deck, Card
from .forms import DeckForm, CardForm
from django.db.models import Q


"""
def edit_collection(request):
    if request.method == "GET":
        query = request.GET.get("q")
        if query:
            decks = Deck.objects.filter(user=request.user, title__icontains=query)
        else:
            decks = Deck.objects.filter(user=request.user)
        return render(request, "edit_collection.html", {"decks": decks})
"""


@login_required
def edit_collection(request):
    decks = Deck.objects.filter(user=request.user)
    if request.method == "GET":
        query = request.GET.get("q")
        if query:
            decks = Deck.objects.filter(
                Q(user=request.user, title__icontains=query)
                | Q(user=request.user, description__icontains=query)
            )
        else:
            # Provide recommendations when no search query is provided
            decks = Deck.objects.filter(user=request.user).order_by("-created_at")[
                :5
            ]  # Example: Show 5 most recent decks
    return render(request, "home.html", {"decks": decks})


@login_required
def create_deck(request):
    if request.method == "POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.user = request.user
            deck.save()
            return redirect("home")  # Redirect to the collection page
    else:
        form = DeckForm()
    return render(request, "edit_deck.html", {"form": form})


@login_required
def edit_deck(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    if request.method == "POST":
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DeckForm(instance=deck)
    return render(request, "edit_deck.html", {"form": form, "deck": deck})


@login_required
def delete_deck(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    deck.delete()
    return redirect("home")


@login_required
def create_card(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    if request.method == "POST":
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.deck = deck
            card.save()
            return redirect(
                "edit_deck", deck_id=deck_id
            )  # Redirect back to the edit deck page
    else:
        form = CardForm()
    return render(request, "edit_card.html", {"form": form, "deck": deck})


@login_required
def edit_card(request, deck_id, card_id):
    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    card = get_object_or_404(Card, pk=card_id, deck=deck)
    if request.method == "POST":
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect("edit_deck", deck_id=deck_id)
    else:
        form = CardForm(instance=card)
    return render(request, "edit_card.html", {"form": form, "deck": deck, "card": card})


@login_required
def delete_card(request, deck_id, card_id):
    deck = get_object_or_404(Deck, pk=deck_id, user=request.user)
    card = get_object_or_404(Card, pk=card_id, deck=deck)
    card.delete()
    return redirect("edit_deck", deck_id=deck_id)
