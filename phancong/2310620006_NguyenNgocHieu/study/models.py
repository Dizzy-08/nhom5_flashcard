from django.db import models
from django.contrib.auth.models import User
from collection.models import Deck, Card  # Import Deck and Card models
from django.utils import timezone
from datetime import datetime


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(
        null=True, blank=True
    )  # Allow null for ongoing sessions

    def __str__(self):
        return f"{self.user.username} - {self.deck.title} - {self.started_at}"

    def end_session(self):
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.save()

            # Calculate session duration in minutes
            duration = (self.ended_at - self.started_at).total_seconds() / 60

            # Update profile
            profile = self.user.profile
            profile.update_streak(self.ended_at.date(), duration)

            # Increase level when session is completed
            profile.increase_level()
            # Calculate session duration in minutes
            duration = (self.ended_at - self.started_at).total_seconds() / 60

            # Update profile
            profile = self.user.profile
            profile.update_streak(self.ended_at.date(), duration)

            # Increase level when session is completed
            profile.increase_level()


class CardProgress(models.Model):
    study_session = models.ForeignKey(StudySession, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.study_session} - {self.card} - {self.is_correct}"
