import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.mapping.models import TerrainMap, DigitalTwinSite, TerrainSector

print("=== Digital Twin Sites and Terrain Maps ===\n")
sites = DigitalTwinSite.objects.all()
for site in sites:
    maps = TerrainMap.objects.filter(digital_twin_site=site)
    print(f"Site: {site.slug}")
    print(f"  Name: {site.name}")
    if maps.exists():
        for terrain_map in maps:
            sectors = TerrainSector.objects.filter(terrain_map=terrain_map)
            print(f"  Map: {terrain_map.slug}")
            print(f"    Sectors: {sectors.count()}")
            if sectors.exists():
                first_sector = sectors.first()
                print(f"    Entry sector: {first_sector.sector_id}")
    else:
        print("  No terrain maps")
    print()
