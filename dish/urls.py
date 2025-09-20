from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'restaurant'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='categories'),
    path('menu/', views.menu_view, name='menu'),
    path('dish/<slug:slug>/', views.DishDetailView.as_view(), name='dish_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
