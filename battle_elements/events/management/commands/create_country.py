import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from main.models import Country


class Command(BaseCommand):
    help = 'Imports countries from a JSON file'

    def handle(self, *args, **options):
        json_path = Path(__file__).resolve().parent.parent / 'country.json'
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                countries_data = json.load(file)
                for country in countries_data:
                    Country.objects.update_or_create(
                        country_id=country['id'],
                        defaults={
                            'name': country['name'],
                            'latitude': country.get('latitude'),
                            'longitude': country.get('longitude'),
                            'countryCode': country['countryCode'],
                        }
                    )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported countries from {json_path}'))
        except FileNotFoundError:
            raise CommandError(f'File {json_path} does not exist')
        except Exception as e:
            raise CommandError(f'An error occurred: {str(e)}')
