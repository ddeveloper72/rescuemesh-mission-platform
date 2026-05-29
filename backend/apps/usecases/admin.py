"""
Use case admin configuration.
"""
from django.contrib import admin
from .models import UseCaseTemplate, TerrainProfile, AgentRoleTemplate


class TerrainProfileInline(admin.StackedInline):
    model = TerrainProfile
    extra = 0
    can_delete = False


class AgentRoleTemplateInline(admin.TabularInline):
    model = AgentRoleTemplate
    extra = 1
    fields = ['name', 'role', 'agent_type', 'default_quantity']


@admin.register(UseCaseTemplate)
class UseCaseTemplateAdmin(admin.ModelAdmin):
    list_display = ['slug', 'title', 'priority', 'is_active', 'is_demo', 'created_at']
    list_filter = ['priority', 'is_active', 'is_demo']
    search_fields = ['slug', 'title', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [TerrainProfileInline, AgentRoleTemplateInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('slug', 'title', 'priority', 'summary', 'objective')
        }),
        ('Status', {
            'fields': ('is_active', 'is_demo')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TerrainProfile)
class TerrainProfileAdmin(admin.ModelAdmin):
    list_display = ['use_case', 'terrain_type', 'gps_status', 'simulation_complexity']
    list_filter = ['gps_status', 'simulation_complexity']
    search_fields = ['use_case__title', 'terrain_type']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AgentRoleTemplate)
class AgentRoleTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'use_case', 'role', 'agent_type', 'default_quantity']
    list_filter = ['use_case', 'agent_type', 'role']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
