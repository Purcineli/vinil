from django.urls import path

from .views import (
    EventCreateView,
    EventDetailView,
    EventListView,
    EventToggleActiveView,
    EventUpdateView,
)

app_name = 'events'

urlpatterns = [
    path('', EventListView.as_view(), name='list'),
    path('<int:pk>/', EventDetailView.as_view(), name='detail'),
    path('criar/', EventCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', EventUpdateView.as_view(), name='update'),
    path('<int:pk>/toggle/', EventToggleActiveView.as_view(), name='toggle_active'),
]
