from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

User = get_user_model()

_TAILWIND_INPUT = (
    'rounded-xl border-slate-200 focus:ring-violet-400 px-4 py-3 w-full'
)


class CustomUserCreationForm(UserCreationForm):
    """Formulário de cadastro com campo de e-mail obrigatório."""

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
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('username', 'password1', 'password2'):
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
        user.email = self.cleaned_data['email'].lower()
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
