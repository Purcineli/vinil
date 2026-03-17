from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """Autentica usuários pelo endereço de e-mail em vez do username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user

        return None
