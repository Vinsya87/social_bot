# Generated by Django 5.0.3 on 2024-03-30 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_alter_event_organizer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.TimeField(blank=True, verbose_name='Время окончания'),
        ),
    ]