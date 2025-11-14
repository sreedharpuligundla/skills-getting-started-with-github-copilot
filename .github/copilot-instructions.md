# Copilot Instructions for Mergington High School Activities API

## Project Overview

This is a lightweight FastAPI web application for managing school extracurricular activities. It combines:
- **Backend**: FastAPI REST API with in-memory data storage
- **Frontend**: Vanilla JavaScript + HTML/CSS that communicates with the API
- **Architecture**: Monolithic single-file design intended for educational purposes

## Key Architecture & Data Flow

### Backend Structure (`src/app.py`)
- **FastAPI Application**: Serves both API endpoints and static files
- **In-Memory Database**: Activities stored as a dict with name as key (e.g., `"Chess Club"`)
- **Activity Schema**: Each activity contains `description`, `schedule`, `max_participants`, and `participants` list
- **Static File Mounting**: `/static` directory mounted for HTML/CSS/JS

### Critical Data Flow
1. Frontend loads `index.html`, which initializes from `/static/index.html`
2. `app.js` fetches activities from `GET /activities` on page load
3. User signs up via form → `POST /activities/{activity_name}/signup?email={email}`
4. No validation of max_participants or duplicate emails in current implementation (known limitation)

## API Endpoints & Patterns

| Endpoint | Method | Purpose | Note |
|----------|--------|---------|------|
| `/` | GET | Redirects to static UI | Uses `RedirectResponse` |
| `/activities` | GET | Returns all activities | Returns raw dict; no pagination |
| `/activities/{activity_name}/signup` | POST | Register student for activity | Email passed as query param; name URL-encoded |

**Important**: Activity names are case-sensitive identifiers used directly in URLs. Frontend encodes them with `encodeURIComponent()`.

## Frontend Communication Patterns (`src/static/app.js`)

- **Fetch Pattern**: Uses `fetch()` with absolute paths (e.g., `/activities`)
- **Error Handling**: Displays user-facing error messages in `messageDiv` with class toggling (`success`/`error`)
- **DOM Updates**: Dynamically populates `#activities-list` and `#activity` select dropdown
- **Message Lifecycle**: Success/error messages auto-hide after 5 seconds

## Development & Testing

### Running the Application
```bash
cd src
pip install -r ../requirements.txt
python app.py
```
Server runs on `http://localhost:8000`. API docs at `/docs` (Swagger UI).

### Testing Setup
- Uses pytest (configured in `pytest.ini` with pythonpath=`.`)
- No tests currently exist; test files should import from `src.app`

### Dependencies
- **fastapi**: REST framework
- **uvicorn**: ASGI server (runs via `uvicorn` inside `app.py` if executed directly)

## Project Conventions

1. **Immutability**: This is a learning project—all data is intentionally ephemeral (in-memory, resets on restart)
2. **Simplicity Over Robustness**: No validation of duplicate signups, capacity checks, or persistence
3. **Module Structure**: Single `app.py` file; keep related logic (data models + endpoints) in one place
4. **Naming**: Activity names are unique identifiers; use clear, descriptive names (e.g., "Chess Club")
5. **Static Files**: HTML/CSS/JS all served from `src/static/`; maintain simple vanilla JS (no frameworks)

## Common Tasks for AI Agents

### Adding a New Activity
Edit the `activities` dict in `src/app.py`; include description, schedule, max_participants, and empty participants list.

### Modifying Frontend
Edit `src/static/app.js` for interactivity or `src/static/index.html` for structure. Keep styling in `styles.css`.

### Extending the API
Add new endpoints to `src/app.py` following the existing pattern. Remember to mount any new static assets if needed.

### Debugging
- Check browser console (`F12`) for fetch errors
- Check server logs in terminal for HTTP errors
- Use FastAPI's built-in `/docs` endpoint for manual API testing
