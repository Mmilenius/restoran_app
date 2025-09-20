from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['full_name', 'phone', 'email', 'date', 'time', 'duration', 'guests', 'zone', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'duration': forms.NumberInput(attrs={
                'min': 1,
                'max': 6,
                'class': 'form-control'
            }),
            'guests': forms.NumberInput(attrs={
                'min': 1,
                'max': 20,
                'class': 'form-control'
            }),
            'zone': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Додаткові побажання...'
            }),
        }
        labels = {
            'full_name': 'Повне ім\'я',
            'phone': 'Номер телефону',
            'email': 'Email (необов\'язково)',
            'date': 'Дата',
            'time': 'Час',
            'duration': 'Тривалість (години)',
            'guests': 'Кількість гостей',
            'zone': 'Оберіть бажану зону',
            'notes': 'Додаткові побажання'
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError('Не можна бронювати на минулі дати')
        return date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        duration = cleaned_data.get('duration')
        zone = cleaned_data.get('zone')

        if date and time and duration and zone:
            # Створюємо тимчасовий об'єкт для перевірки
            temp_booking = Booking(
                date=date,
                time=time,
                duration=duration,
                zone=zone
            )

            # Викликаємо метод перевірки доступності
            if not temp_booking.is_available():
                raise forms.ValidationError('Обраний час уже зайнятий. Будь ласка, оберіть інший час або зону.')