from django.db import models

class Comment(models.Model):
    food_rating = models.PositiveSmallIntegerField("Оцінка страв", default=0)
    service_rating = models.PositiveSmallIntegerField("Оцінка сервісу", default=0)
    text = models.TextField("Коментар", blank=True)
    contact = models.CharField("Контакт", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Страви: {self.food_rating}, Сервіс: {self.service_rating}"
