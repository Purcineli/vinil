from django import forms

from .models import Payment

TAILWIND_INPUT = (
    'w-full rounded-xl border border-slate-200 px-4 py-3 '
    'text-slate-800 text-sm focus:outline-none focus:ring-2 '
    'focus:ring-violet-500 focus:border-transparent'
)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method', 'amount']
        widgets = {
            'method': forms.Select(attrs={'class': TAILWIND_INPUT}),
            'amount': forms.NumberInput(attrs={'class': TAILWIND_INPUT}),
        }
        labels = {
            'method': 'Método de pagamento',
            'amount': 'Valor',
        }
