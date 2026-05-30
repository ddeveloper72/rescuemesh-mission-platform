"""
Mapping admin configuration.
"""
from django.contrib import admin
from .models import (
    ExpectedOutputTemplate,
    DigitalTwinSite,
    TerrainMap,
    TerrainSector,
    TerrainPath,
    Waypoint,
    MapArtifact,
)


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


@admin.register(DigitalTwinSite)
class DigitalTwinSiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'site_type', 'country', 'source_name', 'sensitivity_level', 'created_at']
    list_filter = ['site_type', 'sensitivity_level', 'country']
    search_fields = ['name', 'slug', 'description', 'source_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('slug', 'name', 'site_type', 'country', 'description')
        }),
        ('Attribution and Licensing', {
            'fields': ('source_name', 'source_url', 'source_license', 'attribution')
        }),
        ('Sensitivity and Privacy', {
            'fields': ('sensitivity_level', 'notes')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TerrainMap)
class TerrainMapAdmin(admin.ModelAdmin):
    list_display = ['name', 'digital_twin_site', 'coordinate_system', 'source_format', 'created_at']
    list_filter = ['coordinate_system', 'source_format', 'digital_twin_site']
    search_fields = ['name', 'slug', 'origin_label']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('digital_twin_site', 'slug', 'name')
        }),
        ('Coordinate System', {
            'fields': ('coordinate_system', 'origin_label', 'units')
        }),
        ('Source', {
            'fields': ('source_format',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TerrainSector)
class TerrainSectorAdmin(admin.ModelAdmin):
    list_display = ['sector_id', 'label', 'terrain_map', 'sector_type', 'x_m', 'y_m', 'z_m', 'confidence']
    list_filter = ['sector_type', 'terrain_map']
    search_fields = ['sector_id', 'label', 'source_ref']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('terrain_map', 'sector_id', 'label', 'sector_type')
        }),
        ('Position', {
            'fields': ('x_m', 'y_m', 'z_m', 'elevation_m')
        }),
        ('Dimensions', {
            'fields': ('width_m', 'height_m', 'depth_m')
        }),
        ('Quality', {
            'fields': ('confidence', 'source_ref')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TerrainPath)
class TerrainPathAdmin(admin.ModelAdmin):
    list_display = ['from_sector', 'to_sector', 'distance_m', 'path_type', 'traversal_risk', 'confidence']
    list_filter = ['path_type', 'traversal_risk', 'terrain_map']
    search_fields = ['from_sector__sector_id', 'to_sector__sector_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('terrain_map', 'from_sector', 'to_sector')
        }),
        ('Path Characteristics', {
            'fields': ('distance_m', 'bearing_deg', 'vertical_change_m', 'path_type', 'traversal_risk')
        }),
        ('Quality and Requirements', {
            'fields': ('confidence', 'capabilities_required')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    list_display = ['waypoint_id', 'label', 'terrain_map', 'route_group', 'sequence', 'x_m', 'y_m', 'z_m']
    list_filter = ['terrain_map', 'route_group']
    search_fields = ['waypoint_id', 'label', 'route_group']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('terrain_map', 'waypoint_id', 'label')
        }),
        ('Position', {
            'fields': ('x_m', 'y_m', 'z_m')
        }),
        ('Route Information', {
            'fields': ('sequence', 'route_group')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MapArtifact)
class MapArtifactAdmin(admin.ModelAdmin):
    list_display = ['artifact_type', 'digital_twin_site', 'file_format', 'source_license', 'created_at']
    list_filter = ['artifact_type', 'file_format', 'digital_twin_site']
    search_fields = ['file_format', 'local_path', 'external_url', 'attribution']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('digital_twin_site', 'artifact_type', 'file_format')
        }),
        ('Location', {
            'fields': ('local_path', 'external_url')
        }),
        ('Attribution', {
            'fields': ('source_license', 'attribution', 'notes')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
