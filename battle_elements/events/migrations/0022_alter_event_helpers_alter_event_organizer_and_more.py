# Generated by Django 5.0.3 on 2024-04-14 09:21

import django.db.models.deletion
import events.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_alter_event_coordinator'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='helpers',
            field=models.ManyToManyField(blank=True, related_name='event_helpers', to=settings.AUTH_USER_MODEL, verbose_name='Помощники организатора'),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(default=events.models.get_system_organizer_default, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='organized_events', to=settings.AUTH_USER_MODEL, verbose_name='Организатор'),
        ),
        migrations.AlterField(
            model_name='participation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]