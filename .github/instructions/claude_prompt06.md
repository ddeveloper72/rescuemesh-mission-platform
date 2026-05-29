Great progress. Please do a polish and consistency pass on the live simulation dashboard.

Tasks:

1. Add a live Mission Map / Tactical Map panel to the live simulation pages.
   Do not add Three.js or Cesium yet.
   Use a lightweight SVG or HTML/Tailwind tactical map.

2. The map should react to the live Django mission state:
   - agent positions
   - mapped sectors
   - blocked sectors
   - relay chain
   - hazard markers
   - detection markers
   - map coverage
   - confidence
   - use-case-specific layout

3. For Industrial Inspection, show:
   - Plant Room
   - Pipe Gallery
   - Control Cabinet
   - Duct Section
   - Tank Interior
   - Entry Point
   - thermal hotspots
   - gas detection
   - pressure leak
   - static monitoring node

4. For Collapsed Building Search, show:
   - void spaces
   - collapsed/blocked areas
   - accessible areas
   - LiDAR map coverage
   - relay chain
   - thermal/audio/device detection markers

5. For Cave Rescue, show:
   - cave chambers
   - narrow passages
   - junctions
   - relay chain
   - lost/NFC-readable asset marker
   - audio detection marker

6. For Flooded Structure, show:
   - dry/shallow/deep/submerged zones
   - amphibious agent
   - environmental sensor node
   - electrical hazard marker
   - thermal anomaly above waterline

7. Fix summary counters so they match the live mission events and AI analysis.
   In the Industrial Inspection screenshot:
   - Defect Detection shows all zeros even though critical thermal hotspot and pressure leak events exist.
   - Gas Detections shows zero even though methane detection exists.
   Please derive these counters from the live simulation state or events.

8. Add clear visual severity colours for:
   - critical
   - high
   - medium
   - low

9. Keep the existing API shape unless a small additive field is needed.
   Do not break current routes.
   Do not add WebSockets yet.