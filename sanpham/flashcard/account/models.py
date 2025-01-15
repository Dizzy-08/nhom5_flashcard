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

    @property
    def xp_for_next_level(self):
        """Get XP needed for next level"""
        return self.calculate_xp_for_level(self.level + 1)

    def calculate_xp_for_level(self, level):
        """Every 5 levels, XP needed increases by 200"""
        base_xp = 100
        tier = (level - 1) // 5  # Which 5-level tier we're in
        return base_xp + (tier * 200)

    def calculate_level(self):
        """Calculate level based on total XP"""
        if self.xp < 100:
            return 1

        total_xp = 0
        level = 1

        while total_xp <= self.xp:
            level += 1
            total_xp += self.calculate_xp_for_level(level - 1)

        return level - 1

    def add_xp(self, amount):
        """Add XP and check for level up"""
        current_level = self.level
        self.xp += amount
        self.level = self.calculate_level()
        self.save()
        return self.level > current_level

    def update_streak(self, study_date, duration):
        """Update study streak"""
        days_diff = (
            (study_date - self.last_study_date).days if self.last_study_date else 0
        )

        if days_diff == 1:  # Consecutive day
            self.streak += 1
        elif days_diff > 1:  # Missed days
            self.streak = 1

        self.last_study_date = study_date
        self.save()

    def __str__(self):
        return self.user.username
