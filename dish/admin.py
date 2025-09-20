from django.contrib import admin
from .models import Category, Dish
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active', 'created_at']


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'old_price', 'weight',
        'is_available', 'is_popular'
    ]
    list_filter = [
        'category', 'is_available', 'is_popular'
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}