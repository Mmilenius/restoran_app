# carts/urls.py
from django.urls import path
from .views import (
    CartView, AddToCartView, UpdateCartView,
    RemoveFromCartView, ClearCartView
)

app_name = 'carts'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),               # відображення корзини
    path('add/', AddToCartView.as_view(), name='add'),       # додати страву
    path('update/', UpdateCartView.as_view(), name='update'), # змінити кількість
    path('remove/', RemoveFromCartView.as_view(), name='remove'), # видалити страву
    path('clear/', ClearCartView.as_view(), name='clear'),   # очистити корзину
]
