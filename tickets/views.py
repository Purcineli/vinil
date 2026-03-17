from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from events.models import Event

from .forms import TicketTypeForm
from .models import TicketType


class TicketTypeCreateView(LoginRequiredMixin, CreateView):
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'tickets/ticket_type_form.html'

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['event_pk'])

    def form_valid(self, form):
        event = self._get_event()
        if event.organizer != self.request.user:
            raise PermissionDenied
        form.instance.event = event
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('events:detail', kwargs={'pk': self.object.event.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self._get_event()
        return context


class TicketTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'tickets/ticket_type_form.html'

    def get_object(self, queryset=None):
        ticket_type = get_object_or_404(TicketType, pk=self.kwargs['pk'])
        if ticket_type.event.organizer != self.request.user:
            raise PermissionDenied
        return ticket_type

    def get_success_url(self):
        return reverse('events:detail', kwargs={'pk': self.object.event.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        return context
