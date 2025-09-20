from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Booking
from .forms import BookingForm


class BookingView(View):
    def get(self, request):
        form = BookingForm(initial={
            'date': timezone.now().date(),
            'time': timezone.now().time().replace(hour=13, minute=0, second=0),
            'guests': 2,
            'duration': 2
        })

        return render(request, 'booking/booking.html', {
            'form': form,
            'today': timezone.now().date().isoformat()
        })

    def post(self, request):
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)

            # Якщо користувач авторизований, зберігаємо його
            if request.user.is_authenticated:
                booking.user = request.user
                if not booking.email and request.user.email:
                    booking.email = request.user.email

            booking.save()

            messages.success(request,
                             f'Бронювання створено успішно! Ми зв\'яжемося з вами за номером {booking.phone} для підтвердження.'
                             )
            return redirect('booking:booking_success', booking_id=booking.id)

        return render(request, 'booking/booking.html', {
            'form': form,
            'today': timezone.now().date().isoformat()
        })


class BookingSuccessView(View):
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            return render(request, 'booking/booking_success.html', {
                'booking': booking
            })
        except Booking.DoesNotExist:
            messages.error(request, 'Бронювання не знайдено')
            return redirect('booking:booking')


class CheckTimeAvailabilityView(View):
    def get(self, request):
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        duration = int(request.GET.get('duration', 2))
        zone = request.GET.get('zone', 'main_hall')

        try:
            # Конвертуємо строки в дату та час
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()

            # Створюємо тимчасовий об'єкт для перевірки
            temp_booking = Booking(
                date=date,
                time=time,
                duration=duration,
                zone=zone
            )

            is_available = temp_booking.is_available()

            return JsonResponse({
                'available': is_available,
                'message': 'Час доступний' if is_available else 'Час зайнятий'
            })

        except Exception as e:
            return JsonResponse({
                'available': False,
                'message': 'Невірний формат дати або часу'
            })

@method_decorator(csrf_exempt, name='dispatch')
class CreateBookingAPIView(View):
    def post(self, request):
        try:
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)

                if request.user.is_authenticated:
                    booking.user = request.user

                booking.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Бронювання створено успішно',
                    'booking_id': booking.id,
                    'redirect_url': f'/booking/success/{booking.id}/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Помилка валідації',
                    'errors': form.errors
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка: {str(e)}'
            })