from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class Boss(models.Model):
    BOSS_TYPES = [
        ("CTHULHU", "Lord of R'leyh"),
        ("NYARLATHOTEP", "The Faceless"),
        ("HASTUR", "The King in Yellow"),
        ("YOG-SOTHOTH", "The One and The All"),
    ]

    # Boss name templates for random generation
    BOSS_NAMES = {
        "CTHULHU": [
            "Cthulhu",
        ],
        "NYARLATHOTEP": [
            "Nyarlathotep",
        ],
        "HASTUR": [
            "Hastur",
        ],
        "YOG-SOTHOTH": [
            "Yog-sothoth",
        ],
    }

    # Boss descriptions for random generation
    BOSS_DESCRIPTIONS = {
        "CTHULHU": [
            "The most merciful thing in the world, I think, is the inability of the human mind to correlate all its contents. We live on a placid island of ignorance in the midst of black seas of infinity, and it was not meant that we should voyage far. The sciences, each straining in its own direction, have hitherto harmed us little; but some day the piecing together of dissociated knowledge will open up such terrifying vistas of reality, and of our frightful position therein, that we shall either go mad from the revelation or flee from the deadly light into the peace and safety of a new dark age.",
        ],
        "NYARLATHOTEP": [
            "And as the years passed, I found myself changed. The world around me seemed different, distorted, unreal. The faces of my friends and loved ones grew strange and unfamiliar. I felt a growing sense of detachment, of alienation, as if I were no longer truly a part of this world.",
        ],
        "HASTUR": [
            "Along the shore, the cloud waves break, The twin suns sink, beneath the lake, The shadows lengthen, In Carcosa.",
        ],
        "YOG-SOTHOTH": [
            "Yog-Sothoth knows the gate. Yog-Sothoth is the gate. Yog-Sothoth is the key and guardian of the gate. Past, present, future, all are one in Yog-Sothoth.",
        ],
    }

    name = models.CharField(max_length=100)
    boss_type = models.CharField(max_length=20, choices=BOSS_TYPES)
    description = models.TextField()
    max_health = models.PositiveIntegerField()
    current_health = models.PositiveIntegerField()
    damage_per_study = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_reset = models.DateTimeField(auto_now_add=True)
    last_effect_time = models.DateTimeField(default=timezone.now)

    @classmethod
    def create_random_boss(cls):
        """Create a new random boss with scaled difficulty"""
        # Select random boss type
        boss_type = random.choice([t[0] for t in cls.BOSS_TYPES])

        # Get random name and description for the type
        name = random.choice(cls.BOSS_NAMES[boss_type])
        description = random.choice(cls.BOSS_DESCRIPTIONS[boss_type])

        # Create the boss with scaled stats
        return cls.objects.create(
            name=name,
            boss_type=boss_type,
            description=description,
            max_health=1000,
            current_health=1000,
            damage_per_study=500,
        )

    def take_damage(self, damage):
        """Take damage and create new boss if defeated"""
        self.current_health = max(0, self.current_health - damage)
        was_defeated = self.current_health <= 0

        if was_defeated:
            self.is_active = False
            self.save()

            # Create a new random boss
            new_boss = self.create_random_boss()
            print(
                f"New boss appeared: {new_boss.name} ({new_boss.get_boss_type_display()})"
            )
        else:
            self.save()

        return was_defeated

    def apply_effect(self, user_profile):
        if self.boss_type == "CTHULHU":
            return 0.5
        elif self.boss_type == "NYARLATHOTEP":
            user_profile.coin = 0
            user_profile.save()
        elif self.boss_type == "HASTUR":
            return random.uniform(0.1, 0.9)
        elif self.boss_type == "YOG-SOTHOTH":
            user = user_profile.user
            user.username = ""
            user.save()

        self.save()

    def reset_boss(self):
        """Reset boss health if it's a new day"""
        now = timezone.now()
        if (now - self.last_reset).days >= 1:
            self.current_health = self.max_health
            self.is_active = True
            self.last_reset = now
            self.save()

    def __str__(self):
        return f"{self.name} ({self.get_boss_type_display()})"


class BossProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE)
    damage_dealt = models.PositiveIntegerField(default=0)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "boss"]

    def __str__(self):
        return f"{self.user.username}'s progress against {self.boss.name}"
