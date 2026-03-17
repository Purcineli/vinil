from django.contrib import admin

from .models import Ticket, TicketType


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1
    readonly_fields = ['sold_quantity']


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['event', 'name', 'price', 'total_quantity', 'sold_quantity', 'available_quantity']
    list_filter = ['event']
    search_fields = ['name', 'event__name']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['code', 'uuid', 'order_item', 'is_used', 'used_at', 'created_at']
    list_filter = ['is_used']
    search_fields = ['code', 'uuid']
    readonly_fields = ['uuid', 'code', 'is_used', 'used_at', 'created_at', 'updated_at']
