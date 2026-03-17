from django.contrib import admin
from django.urls import path, include

from events.views import DashboardView, HomeView

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', include('accounts.urls')),
    path('eventos/', include('events.urls')),
    path('', include('tickets.urls')),
    path('', include('orders.urls')),
    path('', include('payments.urls')),
]
