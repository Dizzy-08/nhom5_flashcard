# Generated by Django 4.2.17 on 2025-01-15 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_boss_last_effect_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boss',
            name='boss_type',
            field=models.CharField(choices=[('CTHULHU', 'XP Reducer'), ('NYARLATHOTEP', 'Coin Thief'), ('HASTUR', 'Level Drainer'), ('YOG-SOTHOTH', 'Name Changer')], max_length=20),
        ),
    ]
