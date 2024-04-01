from django.core.management.base import BaseCommand
from events.models import BattleType


class Command(BaseCommand):
    help = 'Заполняет поля для событий BS'

    def handle(self, *args, **kwargs):
        event_types = [
            ('БС 0', 'Запланированное не подтвержденное'),
            ('БС 1', 'Одиночная игра без подсчета очков и рейтинга'),
            ('БС 2', 'Одиночная игра с подсчетом очков и рейтинга'),
            ('БС 3', 'Одиночная игра с видео-сопровождением'),
            ('БС 4', 'Мастер-класс'),
            ('БС 5', 'Промоигры'),
            ('БС 6', 'Экспериментальные игры'),
        ]

        for index, (name, description) in enumerate(event_types):
            event_type = f'BS-{index}'
            bt, created = BattleType.objects.get_or_create(
                name=description,
                description=description,
                event_type=event_type)

            if index >= 1:  # БС1, БС2, БС3
                bt.can_be_series = True
            if index >= 2:  # БС2, БС3
                bt.can_be_league = True
            if index >= 3:  # БС2, БС3
                bt.can_be_festival = True

            bt.save()

        self.stdout.write(self.style.SUCCESS('События BS успешно созданы и обновлены'))
