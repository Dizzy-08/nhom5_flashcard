from django import forms
from .models import Deck, Card


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["title", "description"]

    def __init__(self, *args, **kwargs):
        super(DeckForm, self).__init__(*args, **kwargs)

        for fieldname in ["title", "description"]:
            self.fields[fieldname].widget.attrs.update({"class": "input is-success"})


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["front", "back"]
