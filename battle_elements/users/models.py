from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from main.models import City, Country
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    language_code = models.CharField(
        max_length=10,
        verbose_name='Language Code',
        blank=True,
     )
    phone_number = PhoneNumberField(
        'Номер телефона',
        max_length=20,
        blank=True,
        null=True
        )
    telegram_id = models.IntegerField(
        unique=True,
        blank=True,
        null=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Страна',
        null=True)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name='Город',
        blank=True,
        null=True)
    country_travel = models.CharField(
        'Страна - расположение',
        max_length=100,
        blank=True,)
    city_travel = models.CharField(
        'Город - расположение',
        max_length=100,
        blank=True,)
    additional_info = models.TextField(
        'Дополнительная информация',
        blank=True,
        null=True)
    identification = models.BooleanField(
        'Идентификация',
        default=False)
    is_coordinator = models.BooleanField(
        'Координатор',
        default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} {self.last_name}'


class AbstractProfile(models.Model):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    language_code = models.CharField(
        max_length=10,
        verbose_name='Language Code',
        blank=True,
     )
    phone_number = PhoneNumberField(
        'Номер телефона',
        max_length=20,
        blank=True,
        null=True
        )
    telegram_id = models.IntegerField(
        unique=True,
        blank=True,
        null=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    country_travel = models.CharField(
        'Страна - расположение',
        max_length=100,
        blank=True,)
    city_travel = models.CharField(
        'Город - расположение',
        max_length=100,
        blank=True,)
    additional_info = models.TextField(
        'Дополнительная информация',
        blank=True,
        null=True)
    identification = models.BooleanField(
        'Идентификация',
        default=False)

    class Meta:
        abstract = True


# class Profile(AbstractProfile):
#     first_name = models.CharField(_("first name"), max_length=150, blank=True)
#     last_name = models.CharField(_("last name"), max_length=150, blank=True)
#     email = models.EmailField(_("email address"), blank=True)

#     class Meta:
#         verbose_name = 'Учасник'
#         verbose_name_plural = 'Участники'

#     def __str__(self):
#         return self.username if self.username else "No username provided"


class Coordinator(models.Model):
    LEVEL_CHOICES = [(i, str(i)) for i in range(17)]

    coordinator_level = models.IntegerField(
        'Уровень координатора',
        choices=LEVEL_CHOICES,
        default=0
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='coordinator_profile')
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    city = models.ForeignKey(
        City,
        verbose_name='Основной город',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    cities = models.ManyToManyField(
        City,
        blank=True,
        verbose_name='Города ответственности',
        related_name='coordinators'
    )

    class Meta:
        verbose_name = 'Координатор'
        verbose_name_plural = 'Координаторы'

    def __str__(self):
        return self.user.username if self.user.username else "No username provided"
