from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):

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
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
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
    country = models.CharField(
        'Страна',
        max_length=100,
        blank=True,)
    city = models.CharField(
        'Город',
        max_length=100,
        blank=True,)
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


class Profile(AbstractProfile):
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)

    class Meta:
        verbose_name = 'Учасник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return self.username if self.username else "No username provided"


class Coordinator(AbstractProfile):
    LEVEL_CHOICES = [(i, str(i)) for i in range(17)]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    coordinator_level = models.IntegerField(
        'Уровень координатора',
        choices=LEVEL_CHOICES,
        default=0
    )

    class Meta:
        verbose_name = 'Координатор'
        verbose_name_plural = 'Координаторы'

    def __str__(self):
        return self.user.username

