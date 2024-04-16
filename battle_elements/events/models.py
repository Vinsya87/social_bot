from django.db import models
from main.models import City, Config, Country
from users.models import Coordinator, User


class EventTypeAbs(models.Model):
    name = models.CharField(
        'Название события',
        max_length=100,
        blank=True,
        null=True
    )
    description = models.TextField(
        'Описание события',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Тип события'
        verbose_name_plural = 'Типы событий'
        abstract = True

    def __str__(self):
        return self.name


class EventType(EventTypeAbs):

    class Meta:
        verbose_name = 'Тип события'
        verbose_name_plural = 'Типы событий'

    def __str__(self):
        return self.name


class BattleType(EventTypeAbs):
    EVENT_TYPES = [(f'BS-{i}', f'BS-{i}') for i in range(7)]
    event_type = models.CharField(
        verbose_name='Тип события',
        max_length=5,
        choices=EVENT_TYPES,
        default='BS-0'
    )
    can_be_series = models.BooleanField(
        'Могут объединяться в серии', default=False)
    can_be_league = models.BooleanField(
        'Могут объединяться в лигу', default=False)
    can_be_festival = models.BooleanField(
        'Могут объединяться в фестиваль', default=False)

    class Meta:
        verbose_name = 'Тип битвы'
        verbose_name_plural = 'Типы битв - СТИХИИ'

    def __str__(self):
        return self.name


def get_system_organizer_default():
    """
    Возвращает ID системного организатора по умолчанию.
    Эта функция будет вызвана при создании нового объекта Event, если
    значение для 'organizer' не предоставлено.
    """
    config = Config.objects.first()
    return config.system_organizer if config else None


class Event(models.Model):
    name = models.CharField(
        'Название события',
        max_length=100
    )
    description = models.TextField(
        'Описание события',
        blank=True,
    )
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
    address = models.CharField('Точный адрес', max_length=255)
    start_date = models.DateField('Дата начала')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField(
        'Время окончания',
        blank=True,
        null=True
        )
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=get_system_organizer_default,
        related_name='organized_events',
        verbose_name='Организатор')
    coordinator = models.ForeignKey(
        Coordinator,
        on_delete=models.CASCADE,
        related_name='coordinated_events',
        verbose_name='Координатор',
        blank=True,
        null=True)
    status = models.CharField(
        'Статус события',
        max_length=20,
        choices=[
            ('planned', 'Запланировано'),
            ('active', 'Активно'),
            ('completed', 'Завершено')
        ],
        default='planned'
    )
    is_active = models.BooleanField(
        'Активное',
        default=False)
    helpers = models.ManyToManyField(
        User,
        blank=True,
        related_name='event_helpers',
        verbose_name='Помощники организатора'
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.name

    def get_status_display(self):
        """
        Возвращает человекочитаемое значение статуса
        """
        return dict(self._meta.get_field('status').choices)[self.status]


class Role(models.Model):
    name = models.CharField(
        'Название роли',
        max_length=100)
    description = models.TextField(
        'Описание роли')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class Participation(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='Событие'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='Роль участника в событии'
    )
    confirmation = models.BooleanField(
        'Подтверждение участия',
        default=False
    )

    class Meta:
        verbose_name = 'Участники в событии'
        verbose_name_plural = 'Участники в событиях'


class BattleFormat(models.Model):
    name = models.CharField('Название формата битвы', max_length=50)

    class Meta:
        verbose_name = 'Формат битвы'
        verbose_name_plural = 'Форматы битвы'

    def __str__(self):
        return self.name


class ElementalBattle(Event):
    gathering_time = models.TimeField(
        'Время сбора на битву',
        default='0:30')
    photographer = models.BooleanField(
        'Наличие фотографа',
        default=False)
    rated_game = models.BooleanField(
        'Рейтинговая игра',
        default=False)
    battle_format = models.ForeignKey(
        BattleFormat,
        on_delete=models.CASCADE,
        verbose_name='Формат битвы'
    )
    battle_type = models.ForeignKey(
        BattleType,
        on_delete=models.CASCADE,
        verbose_name='Тип битвы'
    )

    class Meta:
        verbose_name = 'Битва стихий'
        verbose_name_plural = 'Битвы стихий'

    def __str__(self):
        return self.name


class Series(models.Model):
    name = models.CharField('Название серии', max_length=100)
    events = models.ManyToManyField(
        Event,
        verbose_name='События в серии',
        related_name='series')

    class Meta:
        verbose_name = 'Серия'
        verbose_name_plural = 'Серии'

    def __str__(self):
        return self.name


class League(models.Model):
    name = models.CharField('Название лиги', max_length=100)
    series = models.ManyToManyField(
        Series,
        verbose_name='Серии в лиге',
        related_name='leagues')
    events = models.ManyToManyField(
        Event,
        verbose_name='События в лиге',
        related_name='leagues')

    class Meta:
        verbose_name = 'Лига'
        verbose_name_plural = 'Лиги'

    def __str__(self):
        return self.name


class Festival(models.Model):
    name = models.CharField(
        'Название фестиваля',
        max_length=100)
    series = models.ManyToManyField(
        Series,
        verbose_name='Серии в фестивале',
        related_name='festivals')
    leagues = models.ManyToManyField(
        League,
        verbose_name='Лиги в фестивале',
        related_name='festivals')
    events = models.ManyToManyField(
        Event,
        verbose_name='События в фестивале',
        related_name='festivals')

    class Meta:
        verbose_name = 'Фестиваль'
        verbose_name_plural = 'Фестивали'

    def __str__(self):
        return self.name

