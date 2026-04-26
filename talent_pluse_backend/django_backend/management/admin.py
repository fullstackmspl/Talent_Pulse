from django.contrib import admin
from .models import Ticket, Lead

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue_snippet', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('issue',)

    def issue_snippet(self, obj):
        return obj.issue[:50] + "..." if len(obj.issue) > 50 else obj.issue
    issue_snippet.short_description = 'Issue'

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'message')
