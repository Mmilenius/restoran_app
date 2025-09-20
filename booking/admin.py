from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'date', 'time', 'guests', 'status']
    list_filter = ['status', 'date', 'zone']
    search_fields = ['full_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']