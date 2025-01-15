from django.db import models
from django.contrib.auth.models import User
from collection.models import Deck, Card
from django.utils import timezone
from games.models import Boss, BossProgress


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.deck.title} - {self.started_at}"

    def end_session(self):
        """End the study session and return XP gained"""
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.save()

            # Calculate session duration in minutes
            duration = round((self.ended_at - self.started_at).total_seconds() / 60, 2)
            print(f"DEBUG - Session duration: {duration} minutes")

            # Get or create active boss for this user
            boss_progress = BossProgress.objects.filter(
                user=self.user, boss__is_active=True
            ).first()

            if not boss_progress:
                # Create a new boss for this user if they don't have an active one
                new_boss = Boss.create_random_boss()
                boss_progress = BossProgress.objects.create(
                    user=self.user, boss=new_boss, damage_dealt=0
                )

            active_boss = boss_progress.boss
            profile = self.user.profile
            base_xp = 50  # Base XP for completing a session
            xp_gained = base_xp  # Default XP gain

            # Deal damage and check if boss is defeated
            active_boss.take_damage(active_boss.damage_per_study)
            boss_progress.damage_dealt += active_boss.damage_per_study
            boss_progress.save()

            if active_boss.current_health <= 0:
                # Boss defeated!
                profile.boss_defeated += 1
                profile.save()

                # Create new boss for this user
                new_boss = Boss.create_random_boss()
                BossProgress.objects.create(
                    user=self.user, boss=new_boss, damage_dealt=0
                )

            if duration > 2:
                xp_gained -= 40
            elif duration > 1:
                xp_gained -= 20
            elif duration > 0.5:
                xp_gained -= 10
            elif duration < 0.2:
                xp_gained += 30

            if profile.total_study_minutes > 5:
                xp_gained += 10
            elif profile.total_study_minutes > 10:
                xp_gained += 20

            # Apply boss ability effects
            xp_multiplier = active_boss.apply_effect(profile)

            # Apply XP reduction if the boss is CTHULHU
            if xp_multiplier:
                xp_gained = int(base_xp * xp_multiplier)

            # Add XP and update streak
            profile.add_xp(xp_gained)
            profile.update_streak(self.ended_at.date(), duration)

            return xp_gained


class CardProgress(models.Model):
    study_session = models.ForeignKey(StudySession, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.study_session} - {self.card} - {self.is_correct}"
