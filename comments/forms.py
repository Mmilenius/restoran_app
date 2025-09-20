from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['food_rating', 'service_rating', 'text', 'contact']
        widgets = {
            'food_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'service_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={'placeholder': 'Ваш відгук'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Ваші контакти (необов’язково)'}),
        }
