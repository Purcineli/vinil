from django.db import models
from simple_history.models import HistoricalRecords


class Payment(models.Model):
    METHOD_CASH = 'cash'
    METHOD_PIX = 'pix'
    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_DEBIT_CARD = 'debit_card'
    METHOD_MERCADOPAGO = 'mercadopago'

    METHOD_CHOICES = [
        (METHOD_CASH, 'Dinheiro'),
        (METHOD_PIX, 'PIX'),
        (METHOD_CREDIT_CARD, 'Cartão de Crédito'),
        (METHOD_DEBIT_CARD, 'Cartão de Débito'),
        (METHOD_MERCADOPAGO, 'MercadoPago'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_CONFIRMED, 'Confirmado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    # Status brutos retornados pela API do MercadoPago — usados para mapeamento
    MP_STATUS_APPROVED = 'approved'
    MP_STATUS_PENDING = 'pending'
    MP_STATUS_IN_PROCESS = 'in_process'
    MP_STATUS_REJECTED = 'rejected'
    MP_STATUS_CANCELLED = 'cancelled'
    MP_STATUS_REFUNDED = 'refunded'
    MP_STATUS_CHARGED_BACK = 'charged_back'

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='pedido',
    )
    method = models.CharField(
        'método',
        max_length=20,
        choices=METHOD_CHOICES,
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    amount = models.DecimalField(
        'valor',
        max_digits=10,
        decimal_places=2,
    )
    paid_at = models.DateTimeField(
        'pago em',
        null=True,
        blank=True,
    )

    # --- Campos MercadoPago ---
    # ID da preferência de pagamento criada no Checkout Pro
    mp_preference_id = models.CharField(
        'ID preferência MP',
        max_length=100,
        blank=True,
        null=True,
    )
    # ID do pagamento confirmado pelo MP (chega via webhook ou redirect)
    mp_payment_id = models.CharField(
        'ID pagamento MP',
        max_length=100,
        blank=True,
        null=True,
    )
    # Status bruto do MP (approved/pending/rejected/etc.) — para auditoria
    mp_status = models.CharField(
        'status MP',
        max_length=50,
        blank=True,
        null=True,
    )
    # Detalhe do status MP (ex: cc_rejected_insufficient_amount) — para exibir
    # ao usuário o motivo de recusa sem expor detalhes internos
    mp_status_detail = models.CharField(
        'detalhe status MP',
        max_length=100,
        blank=True,
        null=True,
    )
    # Número de parcelas escolhido no Checkout Transparente
    mp_installments = models.PositiveSmallIntegerField(
        'parcelas',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'pagamento'
        verbose_name_plural = 'pagamentos'

    def __str__(self):
        return f'Pagamento #{self.pk} — Pedido #{self.order.pk}'
