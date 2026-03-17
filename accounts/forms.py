import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

User = get_user_model()

_TAILWIND_INPUT = (
    'rounded-xl border-slate-200 focus:ring-violet-400 px-4 py-3 w-full'
)


class CustomUserCreationForm(UserCreationForm):
    """Formulário de cadastro usando apenas e-mail — sem campo username."""

    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': _TAILWIND_INPUT,
            'placeholder': 'seu@email.com',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # username is not in fields, but UserCreationForm.Meta still references it
        # on the parent Meta; ensure it is removed from the rendered field list.
        self.fields.pop('username', None)
        for field_name in ('password1', 'password2'):
            self.fields[field_name].widget.attrs.update({'class': _TAILWIND_INPUT})

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Este e-mail já está cadastrado. Tente fazer login.'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].lower()
        user.email = email
        # Generate a unique username from the local part of the e-mail address.
        # A short random suffix guarantees uniqueness without exposing the full e-mail.
        base = email.split('@')[0][:20]
        suffix = uuid.uuid4().hex[:8]
        user.username = f'{base}_{suffix}'
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formulário de login com label do campo username alterado para E-mail."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'E-mail'
        self.fields['username'].widget = forms.EmailInput(attrs={
            'class': _TAILWIND_INPUT,
            'placeholder': 'seu@email.com',
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': _TAILWIND_INPUT,
            'placeholder': 'Sua senha',
        })
