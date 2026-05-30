# ADR-0004: Generated Media Demo Mode

**Status:** Accepted

**Date:** 2026-05-29

**Decision Makers:** Core Development Team

---

## Context

The RescueMesh Mission Platform needs to demonstrate realistic mission media artifacts (images, audio, spectrograms) for simulations, demos, and development. We must decide between:

1. Requiring S3/object storage infrastructure from day one
2. Implementing generated media for MVP with future migration path to real storage

The platform follows a "simulation-first" philosophy where no real hardware is required for core features.

---

## Decision

**We will implement a generated media system for the MVP that creates synthetic media on demand, with a clear migration path to S3/object storage for real operational deployments.**

### Implementation Approach

**Demo Mode (Current MVP):**
- Python code generates synthetic images using Pillow
- Python generates synthetic audio using the wave module
- Lazy generation: Media created only when requested
- File caching in `media/generated/` directory
- No external dependencies or cloud services required
- Docker-friendly with writable volume for cache

**Future Operational Mode:**
- S3/object storage for captured media from real missions
- Database stores metadata and references
- Same API shape maintained for frontend compatibility
- Configuration-based switch between generated and real media

### Generated Media Types

**Images:**
- Low-light / night vision scenes
- Thermal camera frames with hotspot detection
- Underwater / murky water views
- Industrial inspection imagery
- Dusty rubble / collapsed structure scenes
- Last-good-frame with signal degradation effects

**Audio:**
- Knocking sounds (SOS patterns, regular intervals)
- Tapping audio (higher frequency, sharper)
- Voice-like placeholder audio
- Static / interference
- Ambient environmental sounds

**Spectrograms:**
- Visual frequency analysis of audio clips
- Time-domain representation
- Confidence and signal quality overlays

---

## Consequences

### Positive

**Development Velocity:**
- No S3 setup required during development
- Faster iteration without cloud infrastructure
- Reduced complexity for local development

**Cost Efficiency:**
- Zero cloud storage costs during MVP and demo phases
- No data egress charges
- Predictable development costs

**Portability:**
- Platform runs completely offline
- Easy to package and distribute
- Docker containers are self-contained
- Demo presentations work without internet

**Reproducibility:**
- Same media generated for same mission scenarios
- Consistent demo behavior across environments
- Deterministic testing possible
- Training scenarios repeatable

**Simplicity:**
- No authentication/authorization for storage
- No bucket policies or IAM configuration
- No CDN setup
- Reduced moving parts

### Negative

**Limited Realism:**
- Generated media is synthetic, not actual mission data
- AI models trained on generated data may not generalize to real sensors
- Demo audiences may notice synthetic artifacts
- Quality limited by generation algorithms

**Performance:**
- On-demand generation adds latency (mitigated by caching)
- CPU usage for image/audio generation
- Disk I/O for cache management

**Migration Effort:**
- Future transition to S3 requires backend changes
- Database schema additions for real media metadata
- Testing required for both generated and real modes

**Scaling:**
- Generated media cache grows with usage
- Not suitable for large-scale real-world deployments
- Multi-tenant scenarios need isolation or separate caches

---

## Alternatives Considered

### Alternative 1: S3/Object Storage from Day One

**Pros:**
- Production-ready from start
- Scalable to large datasets
- Industry-standard approach

**Cons:**
- Requires AWS/Azure/GCP account and configuration
- Cloud costs during development
- More complex local development setup
- Internet dependency for demos
- Authentication/authorization overhead

**Rejection Reason:** Violates simulation-first principle; adds unnecessary complexity for MVP.

### Alternative 2: SQLite BLOB Storage

**Pros:**
- No external dependencies
- Simple database integration
- Single-file portability

**Cons:**
- Database bloat with media files
- Poor performance for large media
- Difficult to serve media directly
- Not a migration path to S3

**Rejection Reason:** SQLite not designed for large binary storage; limits future scalability.

### Alternative 3: Git LFS for Media

**Pros:**
- Version-controlled media assets
- Git workflow integration
- Shareable across team

**Cons:**
- Static media only, not dynamically generated
- Repository size concerns
- LFS setup complexity
- Not suitable for real mission media

**Rejection Reason:** Doesn't solve on-demand generation requirement; not a path to operational media storage.

---

## Implementation Notes

### API Endpoints

```
GET /api/v1/missions/{mission_id}/generated-media/
    Returns metadata for all generated media

GET /api/v1/generated-media/{media_id}/preview/
    Serves generated image preview (PNG)

GET /api/v1/generated-media/{media_id}/audio/
    Serves generated audio file (WAV)

GET /api/v1/generated-media/{media_id}/spectrogram/
    Serves spectrogram visualization (PNG)
```

### Cache Directory Structure

```
media/generated/
  images/          # PNG images
  audio/           # WAV audio files
  spectrograms/    # PNG spectrograms
```

### Future Migration Path

When transitioning to real mission media:

1. Add S3 configuration to Django settings
2. Implement media upload service
3. Update media model to reference S3 keys
4. Add `MEDIA_MODE` environment variable: `generated` or `s3`
5. Frontend API remains unchanged
6. Backend serves from S3 when mode is `s3`
7. Keep generated mode available for demos and testing

---

## Monitoring and Maintenance

**Cache Management:**
- Periodic cleanup of old generated media
- Cache size monitoring
- Regeneration on corruption detection

**Quality Improvement:**
- Iteratively improve generation algorithms
- Add more variation to generated media
- Incorporate user feedback on realism

**Documentation:**
- Clearly mark demo media as generated
- Document quality limitations
- Provide examples of real vs. generated media

---

## Related Decisions

- [ADR-0002: Simulation-First Approach](ADR-0002-simulation-first.md)
- [ADR-0005: MeshStatic Before MeshCore](ADR-0005-meshstatic-before-meshcore.md)

---

## References

- Pillow Documentation: https://pillow.readthedocs.io/
- Python wave module: https://docs.python.org/3/library/wave.html
- Django Media Files: https://docs.djangoproject.com/en/5.0/topics/files/
- AWS S3: https://aws.amazon.com/s3/

---

**Status:** Active  
**Review Date:** Q3 2026 (reassess when approaching real mission integration)
