from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from carts.models import Cart, CartItem

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('preparing', 'Готується'),
        ('ready', 'Готово до видачі'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано'),
    ]

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Корзина')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Користувач')
    )
    table_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name=_('Номер столика')
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Загальна сума')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Статус замовлення')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата створення')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата оновлення')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Додаткові примітки')
    )

    class Meta:
        verbose_name = _('Замовлення')
        verbose_name_plural = _('Замовлення')
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення #{self.id} - Столик {self.table_number}"

    def __str__(self):
        return f"Замовлення #{self.id} - Столик {self.table_number} - {self.get_status_display()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('admin:orders_order_change', args=[str(self.id)])

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Замовлення')
    )
    dish_name = models.CharField(
        max_length=200,
        verbose_name=_('Назва страви')
    )
    dish_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Ціна страви')
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Кількість')
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Загальна сума')
    )


    class Meta:
        verbose_name = _('Позиція замовлення')
        verbose_name_plural = _('Позиції замовлення')

    def __str__(self):
        return f"{self.dish_name} x {self.quantity}"

    def __str__(self):
        return f"{self.dish_name} x {self.quantity} - {self.total_price} ₴"