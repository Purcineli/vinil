from django.urls import path

from .views import TicketTypeCreateView, TicketTypeUpdateView

app_name = 'tickets'

urlpatterns = [
    path('eventos/<int:event_pk>/ingressos/criar/', TicketTypeCreateView.as_view(), name='ticket_type_create'),
    path('ingressos/<int:pk>/editar/', TicketTypeUpdateView.as_view(), name='ticket_type_update'),
]
