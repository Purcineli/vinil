from django.db import models
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
