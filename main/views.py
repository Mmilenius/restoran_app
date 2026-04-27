from django.shortcuts import render
from django.views.generic import TemplateView
from dish.models import Dish

# Create your views here.
class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Головна'
        
        # Отримуємо одну популярну страву для головної сторінки
        random_dish = Dish.objects.filter(is_available=True).order_by('?').first()
        context['random_dish'] = random_dish
        
        return context