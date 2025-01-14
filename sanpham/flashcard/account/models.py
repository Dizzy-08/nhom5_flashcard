from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True)
    xp = models.PositiveIntegerField(default=0)
    coin = models.PositiveIntegerField(default=0)
    boss_defeated = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(default=timezone.now, null=True, blank=True)
    total_study_minutes = models.FloatField(default=0)

    def add_xp(self, amount):
        """Add XP and update level if necessary"""
        self.xp += amount
        self.level = (self.xp // 100) + 1
        self.save()

    def update_streak(self, study_date, study_minutes):
        """Update study streak and minutes"""
        days_diff = (
            (study_date - self.last_study_date).days if self.last_study_date else 0
        )

        # Update streak based on consecutive days
        if self.streak == 0 or days_diff == 1:
            self.streak += 1
        elif days_diff > 1:
            self.streak = 1
        # days_diff == 0 means same day, no streak change needed

        # Reset study minutes on new day
        if days_diff >= 1:
            self.total_study_minutes = 0

        # Update study date and minutes
        self.last_study_date = study_date
        self.total_study_minutes = round(
            self.total_study_minutes + float(study_minutes), 2
        )
        self.save()

    def __str__(self):
        return self.user.username
