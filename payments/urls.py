from django.urls import path

from .views import (
    CheckoutProView,
    PaymentCreateView,
    PaymentFailureView,
    PaymentSuccessPendingView,
    PaymentSuccessView,
    TransparentCheckoutProcessView,
    TransparentCheckoutView,
    WebhookView,
)

app_name = 'payments'

urlpatterns = [
    # --- Checkout Pro (fluxo MercadoPago) ---
    path(
        'pedidos/<int:order_pk>/checkout/',
        CheckoutProView.as_view(),
        name='checkout_pro',
    ),
    # Webhook: csrf_exempt aplicado no dispatch da view
    path(
        'pagamento/webhook/',
        WebhookView.as_view(),
        name='webhook',
    ),
    # URL de retorno sucesso/pendente (back_urls do MP)
    path(
        'pagamento/retorno/sucesso/',
        PaymentSuccessPendingView.as_view(),
        name='payment_success_pending',
    ),
    # URL de retorno falha (back_urls do MP)
    path(
        'pagamento/retorno/falha/',
        PaymentFailureView.as_view(),
        name='payment_failure',
    ),

    # --- Views de detalhe ---
    path(
        'pagamento/<int:pk>/sucesso/',
        PaymentSuccessView.as_view(),
        name='payment_success',
    ),

    # --- Checkout Transparente (Card Payment Brick) ---
    path(
        'pedidos/<int:order_pk>/checkout/cartao/',
        TransparentCheckoutView.as_view(),
        name='checkout_transparent',
    ),
    # AJAX endpoint — receives card token from MercadoPago.js Brick
    path(
        'pedidos/<int:order_pk>/checkout/cartao/processar/',
        TransparentCheckoutProcessView.as_view(),
        name='checkout_transparent_process',
    ),

    # --- Rota legada mantida para compatibilidade ---
    path(
        'pedidos/<int:order_pk>/pagar/',
        PaymentCreateView.as_view(),
        name='payment_create',
    ),
]
