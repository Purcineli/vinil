from django import forms

from .models import Event

_INPUT_CLASSES = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg '
    'focus:outline-none focus:ring-2 focus:ring-violet-500'
)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': _INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': _INPUT_CLASSES, 'rows': 4}),
            'location': forms.TextInput(attrs={'class': _INPUT_CLASSES}),
            'start_date': forms.DateTimeInput(
                attrs={'class': _INPUT_CLASSES, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'end_date': forms.DateTimeInput(
                attrs={'class': _INPUT_CLASSES, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure datetime fields render in the correct HTML5 format
        self.fields['start_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_date'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                'A data de término não pode ser anterior à data de início.'
            )

        return cleaned_data
