from django.db import models


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
