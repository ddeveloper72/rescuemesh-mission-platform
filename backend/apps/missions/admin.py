"""
Mission admin configuration.
"""
from django.contrib import admin
from .models import Mission, MissionEvent


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['mission_id', 'name', 'use_case_template', 'use_case_type', 'status', 'created_at']
    list_filter = ['status', 'use_case_template', 'use_case_type', 'created_at']
    search_fields = ['mission_id', 'name', 'objective']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('mission_id', 'name', 'use_case_template', 'use_case_type', 'status')
        }),
        ('Mission Details', {
            'fields': ('objective', 'terrain_description', 'simulation_seed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MissionEvent)
class MissionEventAdmin(admin.ModelAdmin):
    list_display = ['mission', 'event_type', 'title', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['title', 'description', 'source_agent_id']
    readonly_fields = ['id', 'timestamp']
