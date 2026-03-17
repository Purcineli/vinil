from django.db import models
from simple_history.models import HistoricalRecords


class Payment(models.Model):
    METHOD_CASH = 'cash'
    METHOD_PIX = 'pix'
    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_DEBIT_CARD = 'debit_card'

    METHOD_CHOICES = [
        (METHOD_CASH, 'Dinheiro'),
        (METHOD_PIX, 'PIX'),
        (METHOD_CREDIT_CARD, 'Cartão de Crédito'),
        (METHOD_DEBIT_CARD, 'Cartão de Débito'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_CONFIRMED, 'Confirmado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'pagamento'
        verbose_name_plural = 'pagamentos'

    def __str__(self):
        return f'Pagamento #{self.pk} — Pedido #{self.order.pk}'
