"""
Agent admin configuration.
"""
from django.contrib import admin
from .models import Agent, AgentStateChange


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['agent_id', 'name', 'agent_type', 'state', 'current_mission']
    list_filter = ['agent_type', 'state']
    search_fields = ['agent_id', 'name']


@admin.register(AgentStateChange)
class AgentStateChangeAdmin(admin.ModelAdmin):
    list_display = ['agent', 'mission', 'previous_state', 'new_state', 'timestamp']
    list_filter = ['new_state', 'timestamp']
    search_fields = ['agent__agent_id', 'reason']
