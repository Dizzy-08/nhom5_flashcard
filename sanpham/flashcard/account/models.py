from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User  # Use default user model
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(default=timezone.now, null=True, blank=True)
    total_study_minutes = models.FloatField(default=0)  # To track daily study time

    def add_xp(self, amount):
        self.xp += amount
        # Check if level should increase (every 100 XP)
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.save()

    def update_streak(self, study_date, study_minutes):
        print(f"DEBUG - Current last_study_date: {self.last_study_date}")
        print(f"DEBUG - New study_date: {study_date}")
        print(f"DEBUG - Study minutes: {study_minutes}")
        print(f"DEBUG - Current streak: {self.streak}")

        # If total study time is at least 1 minute
        if self.total_study_minutes >= 0:
            if not self.last_study_date:
                # First time studying
                self.streak = 1
            elif self.last_study_date != study_date:
                # Different day
                if study_date - self.last_study_date == timedelta(days=1):
                    # Consecutive day
                    self.streak += 1
                else:
                    # Not consecutive, reset streak
                    self.streak = 1
                # Reset daily study minutes on new day
                self.total_study_minutes = 0

        # Update study time and date
        self.total_study_minutes = round(
            self.total_study_minutes + float(study_minutes), 2
        )  # Round to 2 decimal places
        # self.total_study_minutes += 1
        self.last_study_date = study_date

        """
        # Update streak logic
        if not self.last_study_date:
            self.streak = 1
        elif self.last_study_date == study_date - timedelta(days=1):
            self.streak += 1
        elif self.last_study_date == study_date:
            pass
        else:
            self.streak = 1
        """

        self.save()

        # Add XP for completing a study session
        self.add_xp(50)
        print(f"DEBUG - New streak: {self.streak}")
        print(f"DEBUG - New total_study_minutes: {self.total_study_minutes}")

    def __str__(self):
        return self.user.username
