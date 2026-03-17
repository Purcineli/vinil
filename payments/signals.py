from django.db import transaction
from django.db.models.signals import post_save

from tickets.models import Ticket

from .models import Payment


def emit_tickets_on_payment_confirmed(sender, instance, created, **kwargs):
    if created or instance.status != Payment.STATUS_CONFIRMED:
        return

    with transaction.atomic():
        instance.order.status = 'confirmed'
        instance.order.save()

        for item in instance.order.items.all():
            if not item.tickets.exists():
                for _ in range(item.quantity):
                    Ticket.objects.create(order_item=item)


post_save.connect(
    emit_tickets_on_payment_confirmed,
    sender=Payment,
    weak=False,
)
