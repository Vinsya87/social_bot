# Generated by Django 5.0.3 on 2024-04-14 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_remove_profile_is_coordinator_user_additional_info_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_coordinator',
            field=models.BooleanField(default=False, verbose_name='Координатор'),
        ),
    ]