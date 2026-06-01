import requests
import json

# Check Digital Twin API endpoints
print("=" * 60)
print("1. Checking Terrain Maps API:")
print("=" * 60)
response = requests.get('http://127.0.0.1:8000/api/v1/mapping/terrain-maps/?site_slug=migovec-primadona-demo')
if response.status_code == 200:
    data = response.json()
    # Handle paginated response
    maps = data.get('results', []) if isinstance(data, dict) else data
    print(f"Found {len(maps)} terrain map(s)")
    for m in maps:
        print(f"  - {m.get('slug')}: {m.get('label')}")
else:
    print(f"Error {response.status_code}: {response.text[:200]}")

print("\n" + "=" * 60)
print("2. Checking Terrain Sectors API:")
print("=" * 60)
response = requests.get('http://127.0.0.1:8000/api/v1/mapping/terrain-sectors/?terrain_map_slug=primadona-entrance-zone')
if response.status_code == 200:
    data = response.json()
    # Handle paginated response
    sectors = data.get('results', []) if isinstance(data, dict) else data
    print(f"Found {len(sectors)} sector(s)")
    for s in sectors[:5]:  # Show first 5
        print(f"  - {s.get('sector_id')}: {s.get('label')} @ ({s.get('x_m')}, {s.get('y_m')}, {s.get('z_m')})")
    if len(sectors) > 5:
        print(f"  ... and {len(sectors) - 5} more")
else:
    print(f"Error {response.status_code}: {response.text[:200]}")

print("\n" + "=" * 60)
print("3. Checking Mission Simulation State:")
print("=" * 60)
response = requests.get('http://127.0.0.1:8000/api/v1/missions/063218cf-7662-4675-8337-edabd204b793/state/')
if response.status_code == 200:
    data = response.json()
    sectors = data.get('sectors', [])
    print(f"Simulation state has {len(sectors)} sector(s)")
    print("Sectors with confidence > 0:")
    for s in sectors:
        if s.get('confidence', 0) > 0:
            print(f"  - {s.get('sector_id')}: confidence={s.get('confidence')}, label={s.get('label')}")
else:
    print(f"Error {response.status_code}: {response.text[:200]}")

