from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_CONFIRMED, 'Confirmado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='comprador',
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    total_amount = models.DecimalField(
        'valor total',
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido #{self.pk}'

    @property
    def is_confirmed(self):
        return self.status == self.STATUS_CONFIRMED

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    def confirm(self):
        self.status = self.STATUS_CONFIRMED
        self.save()

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='pedido',
    )
    ticket_type = models.ForeignKey(
        'tickets.TicketType',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='tipo de ingresso',
    )
    quantity = models.PositiveIntegerField('quantidade')
    unit_price = models.DecimalField(
        'preço unitário',
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'item do pedido'
        verbose_name_plural = 'itens do pedido'

    def __str__(self):
        return f'{self.quantity}x {self.ticket_type} — {self.order}'

    @property
    def subtotal(self):
        return self.quantity * self.unit_price
