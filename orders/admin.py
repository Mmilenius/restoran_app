from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'table_number', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'table_number']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20

    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.username}"
        return "Гість"
    user_info.short_description = 'Користувач'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'dish_name', 'quantity', 'total_price']
    list_filter = ['order__status']  # Фільтруємо по статусу замовлення
    search_fields = ['dish_name', 'order__id']
    readonly_fields = []  # Жодних readonly полів
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')