"""
Mapping admin configuration.
"""
from django.contrib import admin
from .models import ExpectedOutputTemplate


@admin.register(ExpectedOutputTemplate)
class ExpectedOutputTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'use_case', 'output_type', 'display_priority', 'confidence_required', 'human_review_required']
    list_filter = ['use_case', 'output_type', 'confidence_required', 'human_review_required']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('use_case', 'name', 'output_type', 'description')
        }),
        ('Requirements', {
            'fields': ('confidence_required', 'human_review_required')
        }),
        ('Display', {
            'fields': ('display_priority', 'icon_name')
        }),
        ('Schema', {
            'fields': ('output_schema',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
