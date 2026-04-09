from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
# Create your models here.
class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True, verbose_name='Аватар')
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    bonus_points = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), verbose_name='Бонусні бали')
    class Meta:
        db_table = 'user'
        verbose_name = 'Користувача'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return self.username

# Create your models here.
