from django.core.management.base import BaseCommand
from events.models import BattleFormat


class Command(BaseCommand):
    help = 'Create initial battle formats in the database'

    def handle(self, *args, **kwargs):
        battle_formats = ['3x3', '4x4', '5x5']
        for format_name in battle_formats:
            battle_format, created = BattleFormat.objects.get_or_create(name=format_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Battle format "{battle_format.name}" created successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'Battle format "{battle_format.name}" already exists'))
