from django.contrib import admin
from .models import Comment
# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("food_rating", "service_rating", "text", "contact", "created_at")
    list_filter = ("food_rating", "service_rating", "created_at")
    search_fields = ("text", "contact")