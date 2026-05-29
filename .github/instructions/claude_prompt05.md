Great work. Please do a demo polish pass now.

The static demo pages and live Django simulation pages are both useful, but the user journey needs to be clearer.

Please review these routes:

Static/fallback routes:
- /demo/collapsed-building-search
- /demo/cave-rescue
- /demo/flooded-structure
- /demo/industrial-inspection

Live simulation routes:
- /demo/live/collapsed-building-search
- /demo/live/cave-rescue
- /demo/live/flooded-structure
- /demo/live/industrial-inspection

Tasks:

1. On each static demo page, add a clear call-to-action button:
   “Open Live Simulation”
   linking to the matching /demo/live/{slug} route.

2. On each live simulation page, add a smaller link:
   “View Static Profile”
   linking back to /demo/{slug}.

3. Make the DataSourceBadge more explicit:
   - Static pages: “Static fallback profile”
   - Live pages: “Live Django simulation”

4. Ensure the static pages do not look broken or unfinished.
   Remove wording like “Awaiting...” unless it is genuinely useful.
   Prefer wording like:
   - “Static profile view”
   - “Live telemetry available in simulation mode”
   - “Open live simulation to view changing mission data”

5. On the /demo overview page, show each use case as a card with two buttons:
   - View Profile
   - Run Live Simulation

6. Confirm that the following routes all work:
   - /demo
   - /demo/collapsed-building-search
   - /demo/cave-rescue
   - /demo/flooded-structure
   - /demo/industrial-inspection
   - /demo/live/collapsed-building-search
   - /demo/live/cave-rescue
   - /demo/live/flooded-structure
   - /demo/live/industrial-inspection

7. Add a short note to the README explaining the difference between:
   - static profile pages
   - live Django simulation pages

8. Do not add WebSockets yet.
   Do not add Celery yet.
   Keep the HTTP polling simulation architecture.

We now have the core shape of the platform working:

```text
Use case templates
    ↓
Django deterministic simulation
    ↓
Astro live pages
    ↓
Changing mission state, agents, events, sensors, AI analysis
```

The key thing I notice from the screenshot is that this page is still showing:

```text
Local Fallback Data
```

So the screenshot is probably from:

```text
/demo/collapsed-building-search
```

rather than the live Django-backed page:

```text
/demo/live/collapsed-building-search
```

That is fine as long as the distinction is intentional. I would make the static page visually useful, but push users clearly toward the live version.

## What I would ask Claude to do next

The next best step is not WebSockets yet. I’d do a **demo polish and route consolidation pass**.

Give Claude this:

```text
Great work. Please do a demo polish pass now.

The static demo pages and live Django simulation pages are both useful, but the user journey needs to be clearer.

Please review these routes:

Static/fallback routes:
- /demo/collapsed-building-search
- /demo/cave-rescue
- /demo/flooded-structure
- /demo/industrial-inspection

Live simulation routes:
- /demo/live/collapsed-building-search
- /demo/live/cave-rescue
- /demo/live/flooded-structure
- /demo/live/industrial-inspection

Tasks:

1. On each static demo page, add a clear call-to-action button:
   “Open Live Simulation”
   linking to the matching /demo/live/{slug} route.

2. On each live simulation page, add a smaller link:
   “View Static Profile”
   linking back to /demo/{slug}.

3. Make the DataSourceBadge more explicit:
   - Static pages: “Static fallback profile”
   - Live pages: “Live Django simulation”

4. Ensure the static pages do not look broken or unfinished.
   Remove wording like “Awaiting...” unless it is genuinely useful.
   Prefer wording like:
   - “Static profile view”
   - “Live telemetry available in simulation mode”
   - “Open live simulation to view changing mission data”

5. On the /demo overview page, show each use case as a card with two buttons:
   - View Profile
   - Run Live Simulation

6. Confirm that the following routes all work:
   - /demo
   - /demo/collapsed-building-search
   - /demo/cave-rescue
   - /demo/flooded-structure
   - /demo/industrial-inspection
   - /demo/live/collapsed-building-search
   - /demo/live/cave-rescue
   - /demo/live/flooded-structure
   - /demo/live/industrial-inspection

7. Add a short note to the README explaining the difference between:
   - static profile pages
   - live Django simulation pages

8. Do not add WebSockets yet.
   Do not add Celery yet.
   Keep the HTTP polling simulation architecture.
```

## Then I’d improve the “cool factor”

Once the route clarity is done, the next visible upgrade should be the **Mission Map panel**.

Right now it looks good as a placeholder, but the map is where the project can really stand out. I’d ask for an intermediate “fake 3D / tactical map” before true Three.js or Cesium.

For example:

```text
MissionMapPanel v2:
- animated grid background
- sector blocks appearing as mapped
- agents moving between sectors
- relay chain lines
- blocked areas
- danger zones
- confidence overlay
- map coverage animation
- point-cloud count ticker
```

Prompt:

```text
Please upgrade MissionMapPanel before adding real 3D.

Do not add Three.js or Cesium yet. Create a lightweight tactical simulation map using HTML/SVG/CSS/Tailwind and live Django simulation state.

The map should react to mission state:
- show mapped sectors
- show blocked sectors
- show accessible areas
- show agent markers at x/y/z positions
- show relay chain lines
- show degraded/failure markers
- show map coverage percentage
- show confidence percentage
- show point count increasing over time
- show use-case-specific labels and hazards

For collapsed-building-search, make it look like a void-space reconstruction.
For cave-rescue, make it look like tunnel passages.
For flooded-structure, make it show dry/shallow/deep/submerged areas.
For industrial-inspection, make it show plant-room zones, pipes, tanks, and inspection points.

Keep it lightweight and maintainable. Use SVG if helpful. No inline CSS. No new heavy mapping library yet.
```

## My suggested next roadmap

You are here:

```text
✅ Static Astro use case profiles
✅ Django API
✅ Django template/runtime model split
✅ Dynamic deterministic mission simulation
✅ Live pages for all four use cases
✅ Data-source badges
```

Next sequence:

```text
1. Clarify static vs live route experience
2. Upgrade tactical map visualisation
3. Add mission controls to each live page
4. Add better simulated event progression per use case
5. Add exportable mission report JSON/PDF later
6. Add WebSockets only when polling feels limiting
7. Add real 3D point cloud viewer later
```

One important design point: the static fallback pages are still valuable. They are your **mission profile pages**. The live pages are your **mission simulation pages**. So don’t delete the static ones — just rename the mental model:

```text
/demo/{slug}       = Mission Profile
/demo/live/{slug}  = Live Simulation
```

That distinction will make the app feel intentional rather than half-static, half-live.
