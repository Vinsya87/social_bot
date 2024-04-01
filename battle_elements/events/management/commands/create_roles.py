from django.core.management.base import BaseCommand
from events.models import Role


class Command(BaseCommand):
    help = 'Create initial roles in the database'

    def handle(self, *args, **kwargs):
        roles = [
            {'name': 'Оператор', 'description': 'Описание Оператор'},
            {'name': 'Партнер', 'description': 'Описание Партнер'},
            {'name': 'Волонтер', 'description': 'Описание Волонтер '},
            {'name': 'Зритель', 'description': 'Описание Зритель'},
            {'name': 'Тренер', 'description': 'Описание Тренер'},
            {'name': 'Мастер', 'description': 'Описание Мастер'},
            {'name': 'Ведущий', 'description': 'Описание Ведущий'},
            {'name': 'Рефери', 'description': 'Описание Рефери'},
            {'name': 'Хранитель', 'description': 'Описание Хранитель'},
            {'name': 'Фотограф', 'description': 'Описание Фотограф'},
            {'name': 'Участник', 'description': 'Описание Участник'},
            
        ]
        for role_data in roles:
            role, created = Role.objects.get_or_create(name=role_data['name'], defaults={'description': role_data['description']})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Role "{role.name}" created successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'Role "{role.name}" already exists'))
