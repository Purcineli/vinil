from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from .forms import EventForm
from .models import Event


class HomeView(ListView):
    queryset = Event.objects.filter(is_active=True).order_by('start_date')[:8]
    template_name = 'public/home.html'
    context_object_name = 'events'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_events_count'] = Event.objects.filter(is_active=True).count()
        context['user_orders_count'] = 0
        context['tickets_issued_count'] = 0
        context['tickets_validated_count'] = 0
        return context


class EventListView(ListView):
    queryset = Event.objects.filter(is_active=True)
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['ticket_types'] = self.object.ticket_types.all()
        except AttributeError:
            context['ticket_types'] = []
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('events:detail', kwargs={'pk': self.object.pk})


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Event, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if event.organizer != request.user:
            return HttpResponseForbidden('Você não tem permissão para editar este evento.')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('events:detail', kwargs={'pk': self.object.pk})


class EventToggleActiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user:
            return HttpResponseForbidden('Você não tem permissão para alterar este evento.')
        event.is_active = not event.is_active
        event.save()
        return redirect(reverse('events:detail', kwargs={'pk': event.pk}))
