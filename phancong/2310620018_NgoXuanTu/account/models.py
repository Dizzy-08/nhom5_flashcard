from django.db import models

from django.contrib.auth.models import User  # Use default user model


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)  # To track daily streaks
    total_study_minutes = models.PositiveIntegerField(
        default=0
    )  # To track daily study time

    def add_xp(self, amount):
        self.xp += amount
        # Check if level should increase (every 100 XP)
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.save()

    def update_streak(self, study_date, study_minutes):
        from datetime import timedelta

        # If studied for at least 5 minutes
        if study_minutes >= 5:
            # Reset minutes if it's a new day
            if self.last_study_date != study_date:
                self.total_study_minutes = 0

            # Update streak logic
            if not self.last_study_date:
                self.streak = 1
            elif self.last_study_date == study_date - timedelta(days=1):
                self.streak += 1
            elif self.last_study_date == study_date:
                pass
            else:
                self.streak = 1

        # Update study time and date
        self.last_study_date = study_date
        self.total_study_minutes += study_minutes
        self.save()

        # Add XP for completing a study session
        self.add_xp(50)

    def __str__(self):
        return self.user.username
