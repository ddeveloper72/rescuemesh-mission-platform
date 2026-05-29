"""
Sensor package template models for RescueMesh platform.

These models define sensor configurations that can be attached to agents
during mission simulations.
"""
from django.db import models
from django.utils import timezone
import uuid


class SensorPackageTemplate(models.Model):
    """
    Template for a sensor package that can be attached to an agent role.
    Examples: LiDAR, thermal camera, microphone array, gas sensor, NFC module
    """
    
    SENSOR_TYPE_CHOICES = [
        ('lidar', 'LiDAR'),
        ('thermal', 'Thermal Camera'),
        ('rgb_camera', 'RGB Camera'),
        ('microphone_array', 'Microphone Array'),
        ('co2_sensor', 'CO2 Sensor'),
        ('gas_sensor', 'Gas Sensor'),
        ('wifi_scanner', 'WiFi Scanner'),
        ('bluetooth_scanner', 'Bluetooth Scanner'),
        ('pressure_sensor', 'Pressure Sensor'),
        ('humidity_sensor', 'Humidity Sensor'),
        ('temperature_sensor', 'Temperature Sensor'),
        ('sonar', 'Sonar'),
        ('imu', 'IMU'),
        ('nfc_module', 'NFC Module'),
        ('water_quality', 'Water Quality Sensor'),
    ]
    
    DATA_FORMAT_CHOICES = [
        ('point_cloud', 'Point Cloud'),
        ('image', 'Image'),
        ('video', 'Video Stream'),
        ('audio', 'Audio Stream'),
        ('scalar', 'Scalar Value'),
        ('json', 'JSON Data'),
        ('binary', 'Binary Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_role = models.ForeignKey(
        'usecases.AgentRoleTemplate',
        on_delete=models.CASCADE,
        related_name='sensor_packages'
    )
    
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPE_CHOICES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    data_format = models.CharField(max_length=50, choices=DATA_FORMAT_CHOICES)
    expected_output = models.TextField(blank=True, help_text="Description of expected sensor output")
    
    # Sensor specifications
    specifications = models.JSONField(
        default=dict,
        help_text="Sensor specs: range, resolution, frequency, accuracy, etc."
    )
    
    # Simulation parameters
    failure_modes = models.JSONField(
        default=list,
        help_text="List of possible failure modes for this sensor"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['agent_role', 'sensor_type']
        verbose_name = 'Sensor Package Template'
        verbose_name_plural = 'Sensor Package Templates'
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.agent_role.name})"
