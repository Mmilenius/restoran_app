from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # ВИДАЛЕНО: поле 'zone'
        fields = ['full_name', 'phone', 'email', 'date', 'time', 'duration', 'guests', 'notes']

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
            'notes': 'Додаткові побажання'
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError('Не можна бронювати на минулі дати')
        return date