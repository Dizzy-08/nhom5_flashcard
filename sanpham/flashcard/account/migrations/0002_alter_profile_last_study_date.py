# Generated by Django 4.2.17 on 2025-01-13 10:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_study_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
