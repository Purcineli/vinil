from django.urls import path

from .views import PaymentCreateView, PaymentSuccessView

app_name = 'payments'

urlpatterns = [
    path(
        'pedidos/<int:order_pk>/pagar/',
        PaymentCreateView.as_view(),
        name='payment_create',
    ),
    path(
        'pagamento/<int:pk>/sucesso/',
        PaymentSuccessView.as_view(),
        name='payment_success',
    ),
]
