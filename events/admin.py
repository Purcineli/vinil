from django.contrib import admin

from tickets.admin import TicketTypeInline

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'organizer', 'start_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['name', 'location']
    list_editable = ['is_active']
    inlines = [TicketTypeInline]
