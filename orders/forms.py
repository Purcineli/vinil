from django import forms


class OrderCreateForm(forms.Form):
    ticket_type_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(
        label='Quantidade',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
    )
