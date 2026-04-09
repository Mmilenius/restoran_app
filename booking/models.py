from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User
from datetime import datetime, timedelta


class Table(models.Model):
    ZONE_CHOICES = [
        ('main_hall', 'Основний зал'),
        ('terrace', 'Альтанка'),
        ('vip', 'VIP-зона'),
    ]

    number = models.PositiveIntegerField(unique=True, verbose_name=_('Номер столика'))
    seats = models.PositiveIntegerField(verbose_name=_('Кількість місць'), default=4)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, verbose_name=_('Зона'), default='main_hall')
    is_vip = models.BooleanField(default=False, verbose_name=_('VIP столик'))

    class Meta:
        verbose_name = _('Столик')
        verbose_name_plural = _('Столики')
        ordering = ['number']

    def __str__(self):
        return f"Стіл {self.number} ({self.get_zone_display()})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Користувач'), null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, verbose_name=_('Столик'))

    full_name = models.CharField(max_length=100, verbose_name=_('Повне ім\'я'))
    phone = models.CharField(max_length=20, verbose_name=_('Номер телефону'))
    email = models.EmailField(verbose_name=_('Email'), blank=True, null=True)

    date = models.DateField(verbose_name=_('Дата бронювання'))
    time = models.TimeField(verbose_name=_('Час бронювання'))
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                           verbose_name=_('Тривалість (години)'), default=2)
    guests = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                         verbose_name=_('Кількість гостей'), default=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Статус'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Додаткові побажання'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата створення'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата оновлення'))

    class Meta:
        verbose_name = _('Бронювання')
        verbose_name_plural = _('Бронювання')
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронювання {self.full_name} - Стіл {self.table.number if self.table else 'Видалено'} ({self.date} {self.time})"

    @property
    def end_time(self):
        return (timezone.datetime.combine(self.date, self.time) + timezone.timedelta(hours=self.duration)).time()