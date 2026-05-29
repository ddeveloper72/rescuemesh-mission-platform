"""
Sensor admin configuration.
"""
from django.contrib import admin
from .models import SensorPackageTemplate


@admin.register(SensorPackageTemplate)
class SensorPackageTemplateAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'agent_role', 'sensor_type', 'data_format']
    list_filter = ['sensor_type', 'data_format', 'agent_role__use_case']
    search_fields = ['display_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('agent_role', 'sensor_type', 'display_name', 'description')
        }),
        ('Configuration', {
            'fields': ('data_format', 'expected_output', 'specifications', 'failure_modes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
