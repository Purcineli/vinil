from django.urls import path

from .views import HomeView

app_name = 'events'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    # path('<int:pk>/', EventDetailView.as_view(), name='detail'),  # Sprint 3
]
