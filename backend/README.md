# RescueMesh Backend

Django backend for the RescueMesh Mission Platform.

## Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## API Endpoints

- `/api/v1/missions/` - Mission management
- `/api/v1/agents/` - Agent management
- `/api/v1/telemetry/` - Telemetry data
- `/api/v1/ai-prompts/` - AI prompt generation

## Apps

- **missions** - Core mission management and simulation
- **agents** - Autonomous agents (drones, robots, sensors)
- **assets** - Hardware assets and components
- **telemetry** - Real-time telemetry data
- **ai_prompts** - AI prompt generation
- **ai_results** - AI analysis results
- **reports** - Mission reports
