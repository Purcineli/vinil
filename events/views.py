from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

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
