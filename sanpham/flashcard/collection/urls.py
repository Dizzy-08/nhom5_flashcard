from django.urls import path
from . import views

urlpatterns = [
    path("", views.edit_collection, name="edit_collection"),
    path("create_deck/", views.create_deck, name="create_deck"),
    path("<int:deck_id>/edit/", views.edit_deck, name="edit_deck"),
    path("<int:deck_id>/delete/", views.delete_deck, name="delete_deck"),
    path("<int:deck_id>/create_card/", views.create_card, name="create_card"),
    path("<int:deck_id>/<int:card_id>/edit/", views.edit_card, name="edit_card"),
    path("<int:deck_id>/<int:card_id>/delete/", views.delete_card, name="delete_card"),
]
