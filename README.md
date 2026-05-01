# NPS Hikes Python SDK

A typed Python client for the [NPS Hikes trail API](https://seanangio-nps-hikes.onrender.com/docs), providing access to National Park hiking trail data with Pydantic models, IDE autocomplete, and meaningful error handling.

## Install

```bash
# From GitHub
pip install git+https://github.com/seanangio/nps-hikes-python-sdk.git

# Local development (editable)
git clone https://github.com/seanangio/nps-hikes-python-sdk.git
cd nps-hikes-python-sdk
pip install -e ".[dev]"
```

**Note:** The API is hosted on Render's free tier, which sleeps after inactivity.
The first request may take up to ~60 seconds while the server cold-starts.
Subsequent requests are fast. The default client timeout is 120 seconds to
accommodate this.

## Quickstart

```python
from nps_hikes import Client

client = Client()

# Get all parks
parks = client.get_parks(visited=True)
for park in parks.parks:
    print(f"{park.park_name} ({park.park_code})")

# Get trails with filtering
trails = client.get_trails(park_code="yose", min_length_mi=5.0)
for trail in trails.trails:
    print(f"{trail.trail_name}: {trail.length_miles} mi")

# Get a park summary
summary = client.get_park_summary("yose")
print(f"{summary.full_name}: {summary.total_trails} trails, {summary.hiked_trails} hiked")
```

## Methods

| Method | Description |
|---|---|
| `get_parks(**filters)` | Get all parks with optional filtering by state, visited status, visit date |
| `get_park_summary(park_code)` | Get detailed summary for a single park with trail statistics |
| `get_trails(**filters)` | Get trails with filtering by park, state, length, source, and pagination |
| `get_hiked_points(**filters)` | Get GPS marker points representing actual hikes |
| `get_stats(**filters)` | Get aggregate hiking statistics across all trails |
| `get_park_stats(**filters)` | Get per-park hiking statistics |

## Error handling

The SDK raises typed exceptions instead of requiring HTTP status code checks:

```python
from nps_hikes import Client, ParkNotFoundError, APIError, ValidationError

client = Client()

try:
    summary = client.get_park_summary("xxxx")
except ParkNotFoundError as e:
    print(f"No park with code: {e.park_code}")
except ValidationError as e:
    print(f"Invalid parameters: {e.detail}")
except APIError as e:
    print(f"Server error {e.status_code}: {e.message}")
```

## Configuration

```python
# Custom base URL (e.g., local development server)
client = Client(base_url="http://localhost:8000")

# Custom timeout (seconds)
client = Client(timeout=60)
```

## Models

All responses are Pydantic v2 models with typed fields and IDE autocomplete. Models are generated from the API's [OpenAPI spec](https://seanangio-nps-hikes.onrender.com/openapi.json) using `datamodel-code-generator`.

To regenerate models after an API change:

```bash
pip install datamodel-code-generator
datamodel-codegen \
    --url https://seanangio-nps-hikes.onrender.com/openapi.json \
    --output src/nps_hikes/models.py \
    --output-model-type pydantic_v2.BaseModel
```

## Development

```bash
# Set Python version (requires pyenv)
pyenv local 3.12.2

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

CC BY-NC-SA 4.0
