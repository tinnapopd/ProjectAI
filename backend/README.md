# Strategic Wargame Backend - Setup Guide

This backend implements a Hybrid AI-Powered Strategic Wargame using Google's Agent Development Kit (ADK).

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Google AI Studio API key OR Google Cloud Project (with Vertex AI enabled)

## Installation

### 1. Create a Virtual Environment (Recommended)

```bash
cd backend
python -m venv .venv

# Activate the virtual environment:
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
```

#### For Google AI Studio (Recommended for Development):

1. Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Update `.env`:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

#### For Google Cloud Vertex AI (Production):

1. Set up a Google Cloud Project
2. Enable Vertex AI API
3. Authenticate with `gcloud auth application-default login`
4. Update `.env`:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

## Running the Backend

### Development Mode

```bash
# Make sure you're in the backend directory
cd backend

# Run with uvicorn
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── schemas.py             # Pydantic models for API
├── .env.example           # Environment variables template
├── api/
│   ├── main.py            # API router configuration
│   └── routes/
│       └── agent.py       # ADK agent endpoints
└── core/
    ├── config.py          # Application configuration
    ├── agent.py           # ADK agent factory functions
    ├── prompt.py          # LLM prompt templates
    ├── game_engine.py     # MaxN search algorithm (advanced)
    └── simple_engine.py   # Simplified game engine
```

## API Endpoints

### Health Check

```bash
GET /api/v1/agent/health
```

### Start Game

```bash
POST /api/v1/agent/start_game
Content-Type: application/json

{
  "business_goal": "maximize market share",
  "our_company": {...},
  "competitors": [...],
  "initial_game_state": {...}
}
```

### Get Strategic Moves

```bash
POST /api/v1/agent/get_strategic_moves?session_id=session_0
```

## Using the ADK Agents

The backend uses three specialized agents:

1. **Strategy Agent** - Generates creative strategic moves
2. **Opponent Agent** - Simulates rational competitor behavior
3. **Evaluator Agent** - Scores game states against business goals

These agents are defined in `core/agent.py` and use Google's Gemini models.

## Troubleshooting

### Import Errors

If you see import errors related to `google.adk`:

```bash
pip install --upgrade google-adk
```

### API Key Issues

- Verify your API key is correct in `.env`
- Check that `GOOGLE_GENAI_USE_VERTEXAI=FALSE` for AI Studio
- Ensure there are no extra spaces in the `.env` file

### Port Already in Use

If port 8000 is busy:

```bash
uvicorn main:app --reload --port 8080
```

## Development with ADK

To use the ADK development UI (optional):

```bash
# From the backend directory
adk web
```

This will start the ADK web interface at `http://localhost:8000/adk`

## Next Steps

1. Test the health endpoint: `curl http://localhost:8000/api/v1/agent/health`
2. Review the API documentation at `http://localhost:8000/docs`
3. Implement the full MaxN search in `core/game_engine.py`
4. Add proper session management (Redis, database, etc.)

## Learn More

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Project Instructions](../instruction.md)
