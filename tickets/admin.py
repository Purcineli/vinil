from django.contrib import admin

from .models import TicketType


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1
    readonly_fields = ['sold_quantity']


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['event', 'name', 'price', 'total_quantity', 'sold_quantity', 'available_quantity']
    list_filter = ['event']
    search_fields = ['name', 'event__name']
