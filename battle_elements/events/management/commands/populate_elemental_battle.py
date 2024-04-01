import random
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from events.models import BattleFormat, BattleType, ElementalBattle
from users.models import Coordinator, Profile


class Command(BaseCommand):
    help = 'Fill the database with test data for ElementalBattle model'

    def handle(self, *args, **kwargs):
        organizer_ids = list(Profile.objects.values_list('id', flat=True))
        battle_type_ids = list(BattleType.objects.values_list('id', flat=True))
        coordinators_data = [
            {'user_id': 1, 'coordinator_level': 5},
            {'user_id': 2, 'coordinator_level': 10},
            {'user_id': 3, 'coordinator_level': 16},
        ]

        for coordinator_data in coordinators_data:
            coordinator, created = Coordinator.objects.get_or_create(**coordinator_data)
        test_data = [
            {
                'name': 'Битва стихий 1',
                'gathering_time': time(hour=18, minute=30),
                'battle_format_id': 1,
                'start_date': date.today() + timedelta(days=10),
                'start_time': time(hour=10, minute=30),
                'end_time': time(hour=12, minute=30),
                'photographer': False,
                'rated_game': True,
                'country': 'Россия',
                'city': 'Москва',
                'address': 'Ленина 1',
                'organizer_id': random.choice(organizer_ids),
                'status': 'completed',
                'coordinator_id': 1,
                'battle_type_id': random.choice(battle_type_ids)
            },
            {
                'name': 'Битва стихий 2',
                'gathering_time': time(hour=19, minute=0),
                'battle_format_id': 2,
                'start_date': date.today() + timedelta(days=11),
                'start_time': time(hour=11, minute=30),
                'end_time': time(hour=12, minute=30),
                'photographer': True,
                'country': 'Россия',
                'city': 'Самара',
                'address': 'Ленина 1',
                'rated_game': False,
                'organizer_id': random.choice(organizer_ids),
                'coordinator_id': 2,
                'status': 'active',
                'battle_type_id': random.choice(battle_type_ids)
            },
            {
                'name': 'Битва стихий 3',
                'gathering_time': time(hour=20, minute=0),
                'battle_format_id': 3,
                'start_date': date.today() + timedelta(days=12),
                'start_time': time(hour=9, minute=30),
                'end_time': time(hour=12, minute=30),
                'photographer': True,
                'country': 'Россия',
                'city': 'Томск',
                'address': 'Ленина 3',
                'rated_game': False,
                'organizer_id': random.choice(organizer_ids),
                'status': 'planned',
                'coordinator_id': 2,
                'battle_type_id': random.choice(battle_type_ids)
            },
        ]
        for data in test_data:
            ElementalBattle.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Test data for ElementalBattle has been successfully added'))
