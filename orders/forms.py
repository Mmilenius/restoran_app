from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number', 'notes']
        widgets = {
            'table_number': forms.NumberInput(attrs={
                'min': 1,
                'max': 50,
                'class': 'form-control',
                'placeholder': 'Введіть номер столика'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Додаткові побажання (необов\'язково)',
                'rows': 3
            })
        }
        labels = {
            'table_number': 'Номер столика',
            'notes': 'Додаткові примітки'
        }