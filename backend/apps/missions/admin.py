"""
Mission admin configuration.
"""
from django.contrib import admin
from .models import Mission, MissionEvent, MissionSimulation


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


@admin.register(MissionSimulation)
class MissionSimulationAdmin(admin.ModelAdmin):
    list_display = ['mission', 'status', 'speed_multiplier', 'started_at', 'updated_at']
    list_filter = ['status', 'speed_multiplier']
    search_fields = ['mission__mission_id', 'mission__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Mission', {
            'fields': ('mission',)
        }),
        ('Simulation Control', {
            'fields': ('status', 'speed_multiplier')
        }),
        ('Time Tracking', {
            'fields': ('started_at', 'paused_at', 'accumulated_elapsed_seconds')
        }),
        ('Configuration', {
            'fields': ('random_seed', 'scenario_config')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
