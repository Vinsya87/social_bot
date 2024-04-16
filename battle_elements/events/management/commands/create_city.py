import json
from pathlib import Path

from django.core.management.base import BaseCommand
from main.models import City, Country


class Command(BaseCommand):
    help = 'Populates City model with data from city.json file'

    def handle(self, *args, **options):
        json_path = Path(__file__).resolve().parent.parent / 'city-fr.json'

        with open(json_path, 'r') as file:
            cities_data = json.load(file)

            for city_data in cities_data['edges']:
                city_info = city_data['node']
                country_code = city_info['countryCode']

                country = Country.objects.get(country_code=country_code)

                City.objects.create(
                    name=city_info['name'],
                    latitude=city_info['latitude'],
                    longitude=city_info['longitude'],
                    country_code=country_code,
                    city_id=city_info['id'],
                    country=country
                )

        self.stdout.write(self.style.SUCCESS(
            'Cities have been successfully created'))
