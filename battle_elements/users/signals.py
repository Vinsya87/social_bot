from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Coordinator, User


@receiver(post_save, sender=User)
def update_coordinator(sender, instance, created, **kwargs):
    if instance.is_coordinator:
        coordinator, created = Coordinator.objects.get_or_create(user=instance)
        group, _ = Group.objects.get_or_create(name='coordinator')

        @transaction.on_commit
        def update_coordinator_commit():
            instance.groups.add(group)
    else:
        group, _ = Group.objects.get_or_create(name='coordinator')

        @transaction.on_commit
        def update_coordinator_commit():
            instance.groups.remove(group)
