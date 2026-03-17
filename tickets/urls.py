from django.urls import path

from .views import (
    MyTicketsListView,
    TicketDetailView,
    TicketTypeCreateView,
    TicketTypeUpdateView,
    TicketValidateView,
)

app_name = 'tickets'

urlpatterns = [
    path('eventos/<int:event_pk>/ingressos/criar/', TicketTypeCreateView.as_view(), name='ticket_type_create'),
    path('ingressos/<int:pk>/editar/', TicketTypeUpdateView.as_view(), name='ticket_type_update'),
    path('meus-ingressos/', MyTicketsListView.as_view(), name='my_tickets'),
    path('ingressos/<uuid:uuid>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('portaria/validar/', TicketValidateView.as_view(), name='ticket_validate'),
]
