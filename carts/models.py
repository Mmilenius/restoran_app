# carts/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from users.models import User
from dish.models import Dish


class Cart(models.Model):
    """Модель корзини користувача або сесії"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Користувач')
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_('Ключ сесії')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата створення')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата оновлення')
    )

    class Meta:
        db_table = 'cart'
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзини')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username}'
        return f'Корзина сесії {self.session_key}'

    @property
    def total_items(self):
        """Загальна кількість товарів у корзині"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Загальна вартість корзини"""
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    """Модель елемента корзини"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Корзина')
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        verbose_name=_('Страва')
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Кількість')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата додавання')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата оновлення')
    )

    class Meta:
        db_table = 'cart_item'
        verbose_name = _('Товар у корзині')
        verbose_name_plural = _('Товари у корзині')
        unique_together = ('cart', 'dish')
        indexes = [
            models.Index(fields=['cart', 'dish']),
        ]

    def __str__(self):
        return f'{self.dish.name} x {self.quantity}'

    def get_total_price(self):
        """Загальна вартість цього товару"""
        return self.dish.price * self.quantity

    def save(self, *args, **kwargs):
        """Видалити товар якщо кількість = 0"""
        if self.quantity <= 0:
            self.delete()
        else:
            super().save(*args, **kwargs)