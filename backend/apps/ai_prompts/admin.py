"""
AI Prompts admin configuration.
"""
from django.contrib import admin
from .models import AIPromptTemplate


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'use_case', 'role', 'is_active', 'requires_human_review']
    list_filter = ['use_case', 'role', 'is_active', 'requires_human_review']
    search_fields = ['name', 'description', 'prompt_text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('use_case', 'name', 'role', 'description')
        }),
        ('Prompts', {
            'fields': ('system_prompt', 'prompt_text')
        }),
        ('Input/Output', {
            'fields': ('input_types', 'output_schema')
        }),
        ('Parameters', {
            'fields': ('temperature', 'max_tokens', 'requires_human_review', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
