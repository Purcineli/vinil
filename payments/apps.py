from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = 'payments'
    verbose_name = 'Pagamentos'

    def ready(self):
        import payments.signals  # noqa: F401
