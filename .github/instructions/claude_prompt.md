Yes, please implement the recommended template-based Django model layer.

Important: do not remove or rewrite the existing runtime models yet. Preserve the current Mission, MissionEvent, Agent, and AgentStateChange models unless a small, safe relationship field is needed.

Add the missing template models across the existing stub apps:

usecases/models.py
- UseCaseTemplate
- TerrainProfile

agents/models.py
- AgentRoleTemplate if this fits best here, or keep it in usecases if cleaner

sensors/models.py
- SensorPackageTemplate

faults/models.py
- FailureProfile

mapping/models.py
- ExpectedOutputTemplate, unless you think outputs belong better in usecases

ai_prompts/models.py
- AIPromptTemplate

The goal is to support a template-driven simulation architecture:

UseCaseTemplate defines the reusable scenario:
- collapsed-building-search
- cave-rescue
- flooded-structure
- industrial-inspection

Mission represents an actual mission run created from a UseCaseTemplate.

Please add appropriate ForeignKey relationships so each template object is linked back to UseCaseTemplate.

Please use:
- clear model names
- readable __str__ methods
- created_at and updated_at timestamps where useful
- JSONField for flexible simulation parameters, effects, schemas, and capabilities
- choices/enums for known fields where sensible
- sensible null/blank choices
- Django admin registration for the new models
- migrations
- seed data or a Django management command to create the four initial use case templates

Please also review the existing Mission model. If it currently stores use_case_type as plain text, add a nullable ForeignKey from Mission to UseCaseTemplate while keeping use_case_type temporarily for backward compatibility. Do not break existing pages or tests.

Please create initial seed data for:
1. Collapsed Building Search
2. Cave Rescue
3. Flooded Structure
4. Industrial Inspection

Each seed should include:
- terrain profile
- recommended agent role templates
- sensor package templates
- expected failure profiles
- expected output templates
- at least one AI prompt template

Please keep the model structure close to the future API shape needed by the Astro frontend demo data.

After implementing, provide:
- files changed
- model summary
- migration names
- how to run migrations
- how to load the seed data
- any assumptions made
- any recommended next steps