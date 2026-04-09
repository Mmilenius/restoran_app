from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from .models import Booking, Table
from .forms import BookingForm


class BookingView(View):
    def get(self, request):
        form = BookingForm(initial={
            'date': timezone.now().date(),
            'time': timezone.now().time().replace(hour=13, minute=0, second=0),
            'guests': 2,
            'duration': 2
        })

        # Групуємо столики за зонами
        tables_by_zone = {
            'main_hall': {
                'name': 'Основний зал',
                'tables': Table.objects.filter(zone='main_hall').order_by('number')
            },
            'terrace': {
                'name': 'Літня тераса',
                'tables': Table.objects.filter(zone='terrace').order_by('number')
            },
            'vip': {
                'name': 'VIP-зона',
                'tables': Table.objects.filter(zone='vip').order_by('number')
            }
        }

        return render(request, 'booking/booking.html', {
            'form': form,
            'tables_by_zone': tables_by_zone,  # Передаємо згруповані столики
            'today': timezone.now().date().isoformat()
        })

    def post(self, request):
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Отримуємо ID столика з прихованого поля
            table_id = request.POST.get('table_id')
            if table_id:
                booking.table_id = table_id

            if request.user.is_authenticated:
                booking.user = request.user
                if not booking.email and request.user.email:
                    booking.email = request.user.email

            booking.save()
            messages.success(request, f'Бронювання створено успішно! Ми зв\'яжемося з вами за номером {booking.phone}.')
            return redirect('booking:booking_success', booking_id=booking.id)

        # Якщо сталася помилка валідації форми, потрібно знову згенерувати групи столів для відображення
        tables_by_zone = {
            'main_hall': {'name': 'Основний зал', 'tables': Table.objects.filter(zone='main_hall').order_by('number')},
            'terrace': {'name': 'Літня тераса', 'tables': Table.objects.filter(zone='terrace').order_by('number')},
            'vip': {'name': 'VIP-зона', 'tables': Table.objects.filter(zone='vip').order_by('number')}
        }

        return render(request, 'booking/booking.html', {
            'form': form,
            'tables_by_zone': tables_by_zone,
            'today': timezone.now().date().isoformat()
        })


class BookingSuccessView(View):
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            return render(request, 'booking/booking_success.html', {'booking': booking})
        except Booking.DoesNotExist:
            messages.error(request, 'Бронювання не знайдено')
            return redirect('booking:booking')


class CheckTimeAvailabilityView(View):
    def get(self, request):
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        duration_str = request.GET.get('duration', '2')

        if not date_str or not time_str:
            return JsonResponse({'success': False, 'message': 'Бракує дати або часу'})

        try:
            duration = int(duration_str) if duration_str else 2
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            try:
                time = datetime.strptime(time_str, '%H:%M:%S').time()
            except ValueError:
                time = datetime.strptime(time_str, '%H:%M').time()

            req_start = datetime.combine(date, time)
            req_end = req_start + timedelta(hours=duration)

            active_bookings = Booking.objects.filter(
                date=date,
                status__in=['pending', 'confirmed']
            )

            occupied_tables = []
            for b in active_bookings:
                b_start = datetime.combine(b.date, b.time)
                b_end = b_start + timedelta(hours=b.duration)

                if req_start < b_end and req_end > b_start:
                    if b.table_id:
                        occupied_tables.append(b.table_id)

            return JsonResponse({'success': True, 'occupied_tables': occupied_tables})

        except Exception as e:
            import traceback
            print("Помилка перевірки часу:", traceback.format_exc())
            return JsonResponse({'success': False, 'message': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class CreateBookingAPIView(View):
    def post(self, request):
        try:
            form = BookingForm(request.POST)
            table_id = request.POST.get('table_id')

            if not table_id:
                return JsonResponse({'success': False, 'message': 'Будь ласка, оберіть столик на карті!'})

            if form.is_valid():
                booking = form.save(commit=False)
                booking.table_id = table_id

                if request.user.is_authenticated:
                    booking.user = request.user
                booking.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Бронювання створено успішно',
                    'redirect_url': f'/booking/success/{booking.id}/'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Помилка валідації', 'errors': form.errors})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Помилка: {str(e)}'})