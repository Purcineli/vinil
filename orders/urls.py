from django.urls import path

from .views import OrderCreateView, OrderDetailView, OrderListView

app_name = 'orders'

urlpatterns = [
    path('pedidos/', OrderListView.as_view(), name='list'),
    path('pedidos/<int:pk>/', OrderDetailView.as_view(), name='detail'),
    path('pedidos/criar/', OrderCreateView.as_view(), name='create'),
]
