from django.core.management.base import BaseCommand
from faker import Faker
from users.models import Profile


class Command(BaseCommand):
    help = 'Creates test users'

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(10):
            email = fake.email()
            phone_number = fake.phone_number()
            first_name = fake.first_name()
            last_name = fake.last_name()
            additional_info = fake.text()
            Profile.objects.create(
                email=email,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                additional_info=additional_info
            )
        self.stdout.write(self.style.SUCCESS('Successfully created test users'))
