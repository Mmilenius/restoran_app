from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.CreateOrderView.as_view(), name='create_order'),
    path('success/<int:order_id>/', views.OrderSuccessView.as_view(), name='order_success'),
    path('list/', views.OrderListView.as_view(), name='order_list'),
    path('api/create/', views.CreateOrderAPIView.as_view(), name='api_create_order'),
]