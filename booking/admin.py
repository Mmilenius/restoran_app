from django.contrib import admin
from .models import Booking, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'seats', 'zone', 'is_vip']
    list_filter = ['zone', 'is_vip']
    search_fields = ['number']
    ordering = ['number']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Додали 'table' замість старих полів
    list_display = ['id', 'full_name', 'phone', 'date', 'time', 'table', 'guests', 'status']

    # Замінили 'zone' на 'table__zone', щоб фільтрувати по зоні обраного столика
    list_filter = ['status', 'date', 'table__zone']

    search_fields = ['full_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']