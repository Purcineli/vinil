from django import forms
from django.core.exceptions import ValidationError

from .models import TicketType

_FIELD_CLASSES = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg '
    'focus:outline-none focus:ring-2 focus:ring-violet-500'
)


class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ['name', 'description', 'price', 'total_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': _FIELD_CLASSES}),
            'description': forms.Textarea(attrs={'class': _FIELD_CLASSES, 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': _FIELD_CLASSES}),
            'total_quantity': forms.NumberInput(attrs={'class': _FIELD_CLASSES}),
        }

    def clean_total_quantity(self):
        total_quantity = self.cleaned_data.get('total_quantity')
        if self.instance.pk:
            if total_quantity < self.instance.sold_quantity:
                raise ValidationError(
                    'A quantidade total não pode ser menor que a quantidade já vendida '
                    f'({self.instance.sold_quantity}).'
                )
        return total_quantity
