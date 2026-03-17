from django.contrib import admin
from django.urls import path, include

from events.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', include('accounts.urls')),
    path('', include('events.urls')),
    path('', include('tickets.urls')),
    path('', include('orders.urls')),
    path('', include('payments.urls')),
]
