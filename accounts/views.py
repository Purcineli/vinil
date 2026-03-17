from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import CustomAuthenticationForm, CustomUserCreationForm


class RegisterView(CreateView):
    """Cadastro de novos usuários."""

    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class CustomLoginView(LoginView):
    """Login via e-mail utilizando o formulário customizado."""

    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    """Logout redirecionando para a página inicial."""

    next_page = '/'


class ProfileView(LoginRequiredMixin, TemplateView):
    """Exibe os dados do usuário autenticado."""

    template_name = 'accounts/profile.html'
