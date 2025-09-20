from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

# Create your models here.
class Category(models.Model):
    """Модель категорії страв"""
    name = models.CharField(
        max_length=100,
        verbose_name=_('Назва категорії')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('URL-назва')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата створення')
    )

    class Meta:
        verbose_name = _('Категорія')
        verbose_name_plural = _('Категорії')

    def __str__(self):
        return self.name


class Dish(models.Model):
    """Модель страви"""
    name = models.CharField(
        max_length=200,
        verbose_name=_('Назва страви')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL-назва')
    )
    description = models.TextField(
        verbose_name=_('Опис страви')
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name=_('Категорія')
    )

    # Ціни
    price = models.DecimalField(
        max_digits=8,
        decimal_places=0,  # Ціни в гривнях без копійок
        validators=[MinValueValidator(0)],
        verbose_name=_('Ціна')
    )
    old_price = models.DecimalField(
        max_digits=8,
        decimal_places=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Стара ціна'),
        help_text=_('Для відображення знижки')
    )

    # Зображення
    image = models.ImageField(
        upload_to='dishes/',
        verbose_name=_('Зображення страви')
    )

    # Характеристики
    weight = models.PositiveIntegerField(
        verbose_name=_('Вага (г)')
    )

    is_popular = models.BooleanField(
        default=False,
        verbose_name=_('Популярна страва')
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Доступна')
    )

    likes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Кількість лайків')
    )

    # Дати
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата створення')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата оновлення')
    )

    class Meta:
        verbose_name = _('Страва')
        verbose_name_plural = _('Страви')
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['is_popular']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def discount_percentage(self):
        """Розрахунок відсотка знижки"""
        if self.old_price and self.old_price > self.price:
            return round(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    @property
    def is_discounted(self):
        """Чи є знижка на страву"""
        return self.old_price and self.old_price > self.price
