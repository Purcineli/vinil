from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['ticket_type', 'quantity', 'unit_price', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'buyer', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
