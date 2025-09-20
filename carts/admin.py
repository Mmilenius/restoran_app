from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    # ВИДАЛИТИ або закоментувати рядок з actions, якщо він є
    # actions = [...]  # Якщо є такий рядок - видаліть його

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'dish', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['dish__name']
    readonly_fields = ['created_at', 'updated_at']
    # ВИДАЛИТИ або закоментувати рядок з actions, якщо він є