from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from tickets.models import TicketType

from .forms import OrderCreateForm
from .models import Order, OrderItem


class OrderCreateView(LoginRequiredMixin, View):
    template_name = 'orders/order_create.html'

    def get(self, request):
        ticket_type_id = request.GET.get('ticket_type_id')
        ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
        form = OrderCreateForm(initial={'ticket_type_id': ticket_type_id})
        return render(request, self.template_name, {
            'form': form,
            'ticket_type': ticket_type,
        })

    def post(self, request):
        form = OrderCreateForm(request.POST)
        if not form.is_valid():
            ticket_type_id = request.POST.get('ticket_type_id')
            ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
            return render(request, self.template_name, {
                'form': form,
                'ticket_type': ticket_type,
            })

        ticket_type_id = form.cleaned_data['ticket_type_id']
        quantity = form.cleaned_data['quantity']

        with transaction.atomic():
            ticket_type = (
                TicketType.objects
                .select_for_update()
                .get(pk=ticket_type_id)
            )

            if ticket_type.available_quantity < quantity:
                messages.error(
                    request,
                    f'Quantidade indisponível. Restam apenas '
                    f'{ticket_type.available_quantity} ingresso(s).',
                )
                return redirect('events:detail', pk=ticket_type.event_id)

            ticket_type.sold_quantity += quantity
            ticket_type.save()

            order = Order.objects.create(
                buyer=request.user,
                status=Order.STATUS_PENDING,
                total_amount=quantity * ticket_type.price,
            )

            OrderItem.objects.create(
                order=order,
                ticket_type=ticket_type,
                quantity=quantity,
                unit_price=ticket_type.price,
            )

        return redirect('orders:detail', pk=order.pk)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).select_related('buyer')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).prefetch_related(
            'items__ticket_type__event',
        )
