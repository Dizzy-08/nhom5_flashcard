# Generated by Django 4.2.17 on 2025-01-14 23:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Boss',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('boss_type', models.CharField(choices=[('XP_REDUCER', 'XP Reducer'), ('COIN_THIEF', 'Coin Thief'), ('LEVEL_DRAINER', 'Level Drainer'), ('NAME_CHANGER', 'Name Changer')], max_length=20)),
                ('description', models.TextField()),
                ('max_health', models.PositiveIntegerField()),
                ('current_health', models.PositiveIntegerField()),
                ('damage_per_study', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_reset', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('item_type', models.CharField(choices=[('HEALTH_POTION', 'Health Potion'), ('XP_BOOST', 'XP Boost'), ('COIN_BOOST', 'Coin Boost'), ('SHIELD', 'Boss Shield'), ('DAMAGE_BOOST', 'Damage Boost')], max_length=20)),
                ('description', models.TextField()),
                ('cost', models.PositiveIntegerField()),
                ('duration', models.PositiveIntegerField(help_text='Duration in minutes')),
                ('effect_value', models.FloatField(help_text="Value of the item's effect")),
            ],
        ),
        migrations.CreateModel(
            name='UserItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('acquired_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False)),
                ('activated_at', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BossProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('damage_dealt', models.PositiveIntegerField(default=0)),
                ('last_interaction', models.DateTimeField(auto_now=True)),
                ('boss', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.boss')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'boss')},
            },
        ),
    ]
