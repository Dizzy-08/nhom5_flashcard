from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class Boss(models.Model):
    BOSS_TYPES = [
        ("CTHULHU", "XP Reducer"),
        ("NYARLATHOTEP", "Coin Thief"),
        ("HASTUR", "Level Drainer"),
        ("YOG-SOTHOTH", "Name Changer"),
    ]

    # Boss name templates for random generation
    BOSS_NAMES = {
        "CTHULHU": [
            "Cthulhu",
            "Lord of R'lyeh",
        ],
        "NYARLATHOTEP": [
            "Nyarlathotep",
            "The Faceless",
        ],
        "HASTUR": [
            "Hastur",
            "The King in Yellow",
        ],
        "YOG-SOTHOTH": [
            "Yog-sothoth",
            "The Lurker at the Thresold",
        ],
    }

    # Boss descriptions for random generation
    BOSS_DESCRIPTIONS = {
        "CTHULHU": [
            "In shadowed R'lyeh, he slumbers, a kraken of cosmic dread, awaiting the hour of mankind's demise.",
            "In the sunken city, beneath the waves, a monstrous god slumbers and dreams. When he wakes, the stars will align, and reality will unravel.",
        ],
        "NYARLATHOTEP": [
            "The whispers grow louder in the shadows, promising power and forbidden knowledge. A cold wind blows, and the stars seem to writhe in the sky.",
            "The carnival arrived in the dead of night, its lights flickering with an unnatural glow. Laughter echoes through the empty streets, a chilling, hollow sound.",
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
            max_health=int(1000),
            current_health=int(1000),
            damage_per_study=int(500),
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
        """Apply the boss's negative effect to the user"""
        now = timezone.now()

        # Only apply daily effects once per day
        if (now - self.last_effect_time).days >= 1:
            if self.boss_type == "CTHULHU":
                return 0.5
            elif self.boss_type == "NYARLATHOTEP":
                user_profile.coin = 0
                user_profile.save()
            elif self.boss_type == "HASTUR":
                if user_profile.level > 1:
                    user_profile.level -= 1
                    user_profile.save()
            elif self.boss_type == "YOG-SOTHOTH":
                user = user_profile.user
                if not user.username.startswith("john_doe_"):
                    user.username = f"john_doe_{random.randint(1000, 9999)}"
                    user.save()

            self.last_effect_time = now
            self.save()

        return 0.5 if self.boss_type == "CTHULHU" else None

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


class Item(models.Model):
    ITEM_TYPES = [
        ("HEALTH_POTION", "Health Potion"),
        ("XP_BOOST", "XP Boost"),
        ("COIN_BOOST", "Coin Boost"),
        ("SHIELD", "Boss Shield"),
        ("DAMAGE_BOOST", "Damage Boost"),
    ]

    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    description = models.TextField()
    cost = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    effect_value = models.FloatField(help_text="Value of the item's effect")

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"


class UserItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    acquired_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.item.name}"

    def activate(self):
        """Activate an item for the user"""
        if self.quantity > 0 and not self.is_active:
            self.is_active = True
            self.activated_at = timezone.now()
            self.quantity -= 1
            self.save()

    def is_effect_active(self):
        """Check if the item's effect is still active"""
        if not self.is_active or not self.activated_at:
            return False

        time_elapsed = timezone.now() - self.activated_at
        return time_elapsed.total_seconds() / 60 < self.item.duration


class BossProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE)
    damage_dealt = models.PositiveIntegerField(default=0)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "boss"]

    def __str__(self):
        return f"{self.user.username}'s progress against {self.boss.name}"
