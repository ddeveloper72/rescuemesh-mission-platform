"""
Fault admin configuration.
"""
from django.contrib import admin
from .models import FailureProfile


@admin.register(FailureProfile)
class FailureProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'use_case', 'affected_component', 'severity', 'trigger_type']
    list_filter = ['use_case', 'severity', 'trigger_type', 'affected_component', 'is_recoverable']
    search_fields = ['name', 'description', 'operator_message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('use_case', 'name', 'description')
        }),
        ('Failure Configuration', {
            'fields': ('affected_component', 'severity', 'trigger_type', 'trigger_conditions')
        }),
        ('Effects', {
            'fields': ('effects', 'operator_message')
        }),
        ('Recovery', {
            'fields': ('is_recoverable', 'recovery_actions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
