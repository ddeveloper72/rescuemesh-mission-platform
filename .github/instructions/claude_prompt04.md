Please update the Astro Mission Demos overview page.

The page currently says the demos use local TypeScript data and that Django integration is future work. That is now outdated because the Django simulation API exists and live demo routes have been implemented.

Please update the demo overview page so it clearly distinguishes between:

1. Static Mission Profile pages
2. Live Django Simulation pages

For each use case card, add two actions:
- View Profile → /demo/{slug}
- Run Live Simulation → /demo/live/{slug}

Use cases:
- collapsed-building-search
- cave-rescue
- flooded-structure
- industrial-inspection

Please update the card wording:
- The status badge can remain “Simulated”
- Add a small data indicator or label showing:
  “Static profile available”
  “Live simulation available”

Please replace the bottom note with:

“Static profile pages use local TypeScript fallback data. Live simulation pages connect to the Django API and show changing mission state, agent telemetry, map coverage, sensor events, failure scenarios, and AI analysis.”

Please update the Demo Features section to say:
- Static mission profile views
- Live Django-backed simulation pages
- Simulated agent battery and signal changes
- Mission map coverage and confidence updates
- Sensor detections and failure events
- AI analyst summaries and human review prompts

Please ensure:
- /demo still works
- all View Profile links work
- all Run Live Simulation links work
- no outdated wording remains that says Django integration is only future work
- styling remains consistent with the existing RescueMesh dark mission-control design
- no inline CSS