import base64
import random
import string
import uuid
from io import BytesIO

import qrcode
from django.db import IntegrityError, models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class TicketType(models.Model):
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='ticket_types',
        verbose_name='evento',
    )
    name = models.CharField('nome', max_length=100)
    description = models.TextField('descrição', blank=True)
    price = models.DecimalField('preço', max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField('quantidade total')
    sold_quantity = models.PositiveIntegerField('quantidade vendida', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['price']
        verbose_name = 'tipo de ingresso'
        verbose_name_plural = 'tipos de ingresso'

    def __str__(self):
        return f'{self.event.name} — {self.name}'

    @property
    def available_quantity(self):
        return self.total_quantity - self.sold_quantity

    @property
    def is_available(self):
        return self.available_quantity > 0


class Ticket(models.Model):
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='item do pedido',
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    code = models.CharField('código', max_length=10, unique=True, blank=True)
    is_used = models.BooleanField('utilizado', default=False)
    used_at = models.DateTimeField('utilizado em', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'ingresso'
        verbose_name_plural = 'ingressos'

    def __str__(self):
        return f'Ingresso {self.code}'

    @staticmethod
    def generate_code():
        return 'VNL-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                self.code = self.generate_code()
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    pass
        else:
            super().save(*args, **kwargs)

    def get_qrcode_base64(self):
        img = qrcode.make(self.code)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def mark_as_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
