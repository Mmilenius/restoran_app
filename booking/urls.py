from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.BookingView.as_view(), name='booking'),
    path('success/<int:booking_id>/', views.BookingSuccessView.as_view(), name='booking_success'),
    path('check-availability/', views.CheckTimeAvailabilityView.as_view(), name='check_availability'),
    path('api/create/', views.CreateBookingAPIView.as_view(), name='api_create_booking'),
]