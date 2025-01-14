# Generated by Django 4.2.17 on 2025-01-13 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_study_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='level',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='profile',
            name='streak',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='total_study_minutes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
