from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from orders.models import Order

from .forms import PaymentForm
from .models import Payment


class PaymentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'payments/payment_form.html'
    form_class = PaymentForm

    def _get_order(self):
        return get_object_or_404(Order, pk=self.kwargs['order_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self._get_order()
        return context

    def form_valid(self, form):
        order = self._get_order()

        if order.buyer != self.request.user:
            raise PermissionDenied

        form.instance.order = order
        form.instance.status = Payment.STATUS_CONFIRMED
        form.instance.paid_at = timezone.now()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('payments:payment_success', kwargs={'pk': self.object.pk})


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_success.html'
    context_object_name = 'payment'

    def get_object(self, queryset=None):
        payment = super().get_object(queryset)

        if payment.order.buyer != self.request.user:
            raise PermissionDenied

        return payment
