from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('details', 'user__username')