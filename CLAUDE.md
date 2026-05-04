# CLAUDE.md

## SDK Plan
See /Users/seanangiolillo/Box Sync/nps-hikes/scratch/sdk-plan.md
for the full implementation plan, architecture decisions, and context.

## Server repo
- Local: /Users/seanangiolillo/Box Sync/nps-hikes/
- API spec: https://seanangio-nps-hikes.onrender.com/openapi.json
- API docs: https://seanangio-nps-hikes.onrender.com/docs

## This repo
- Python SDK wrapping 6 data endpoints from the NPS Hikes API
- Models in `src/nps_hikes/models.py` are generated from the OpenAPI spec
  using `datamodel-code-generator` (not hand-written)
- Install: `pip install -e ".[dev]"`
- Tests: `pytest tests/ -v` (all tests use mocked HTTP, no network needed)

## Key files
- `src/nps_hikes/client.py` -- Client class with 6 methods
- `src/nps_hikes/models.py` -- Pydantic v2 models (auto-generated)
- `src/nps_hikes/exceptions.py` -- Custom exception hierarchy
- `tests/test_client.py` -- Client tests with mocked responses
- `tests/test_models.py` -- Model validation tests

## OpenAPI specs
Versioned snapshots live in `specs/` (e.g., `specs/openapi-2026-05-01.json`).
Save a new snapshot before regenerating models so you can diff changes.

## Regenerating models
When the server API changes, regenerate models:
```bash
datamodel-codegen \
    --url https://seanangio-nps-hikes.onrender.com/openapi.json \
    --output src/nps_hikes/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --use-annotated
```
Or from a local spec file:
```bash
datamodel-codegen \
    --input specs/openapi-2026-05-01.json \
    --output src/nps_hikes/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --use-annotated
```
Then run the post-generation cleanup script:
```bash
python scripts/postgen_cleanup.py src/nps_hikes/models.py
```
This removes unwanted classes (NlqRequest, NlqResponse, ValidationError,
HTTPValidationError), inlines RootModel wrappers, and cleans up imports.

## Automated spec sync
A weekly GitHub Actions workflow (`.github/workflows/sync-spec.yml`) checks
for OpenAPI spec changes every Monday. If the spec has changed, it saves a
new snapshot, regenerates models, runs the cleanup script, and opens a PR.
