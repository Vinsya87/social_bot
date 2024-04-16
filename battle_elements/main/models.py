from django.db import models
from geopy.geocoders import Nominatim


class Config(models.Model):
    site_name = models.CharField(
        max_length=255,
        verbose_name='Название проекта',
        blank=True,
        null=True,
        help_text='Введите название которе будет отображаться в системе'
    )
    system_organizer = models.IntegerField(
        'Системный организатор - ID',
        help_text='Например после удаление организатора события, '
                  'будет указан он в качестве организатора',
        blank=True,
        default=1
    )
    cache = models.IntegerField(
        'Кеширование',
        help_text='Указать число в секундах',
        blank=True,
        default=0
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country_code = models.CharField(max_length=255, unique=True)
    country_id = models.IntegerField(unique=True)

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(self.address)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return self.name.capitalize()


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country_code = models.CharField(max_length=255, unique=False)
    city_id = models.IntegerField(unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='cities')

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(self.address)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name.capitalize()
