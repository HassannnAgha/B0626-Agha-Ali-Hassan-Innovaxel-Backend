# Event Registration System API
**B0626 - Agha Ali Hassan - Innovaxel - Backend**

## Overview
A REST API for an event registration system built with FastAPI and SQLite.
Supports creating events, registering users, viewing events with filtering/sorting,
and cancelling registrations. Handles real-world constraints including race condition
prevention and SQL injection protection.

## Tech Stack
- Python 3.x
- FastAPI
- SQLite (via built-in sqlite3)
- Pydantic v2
- Uvicorn

## Project Structure
├── main.py         # FastAPI app, routes, exception handlers
├── database.py     # SQLite connection, PRAGMA config, table creation
├── schemas.py      # Pydantic request/response models and validators
├── crud.py         # All database logic and queries
├── requirements.txt
└── README.md

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/B0626---Agha-Ali-Hassan---Innovaxel---Backend.git
cd B0626---Agha-Ali-Hassan---Innovaxel---Backend
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Open API docs
http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /api/v1/events | Create a new event |
| GET | /api/v1/events | List all events |
| GET | /api/v1/events/{id} | Get single event |
| POST | /api/v1/events/{id}/register | Register user for event |
| DELETE | /api/v1/registrations/{id} | Cancel registration |

## Query Parameters

| Endpoint | Parameter | Type | Description |
|----------|-----------|------|-------------|
| GET /api/v1/events | upcoming_only | bool | Show only future events |
| GET /api/v1/events | sort_by_date | bool | Sort by event date ascending |
| DELETE /api/v1/registrations/{id} | user_name | string | Name of user cancelling |

## Request Examples

### Create Event
```json
{
  "name": "Tech Conference",
  "total_seats": 50,
  "event_date": "2026-12-01",
  "start_time": "10:30",
  "end_time": "12:30"
}
```

### Register User
```json
{
  "user_name": "Hassan"
}
```

## Design Decisions

### Race Condition Prevention
Two simultaneous registration requests could both read `available_seats = 1`
and both proceed, causing overbooking. This is prevented using an atomic UPDATE:

```sql
UPDATE events 
SET available_seats = available_seats - 1
WHERE id = ? AND available_seats > 0
```

The `WHERE available_seats > 0` is evaluated atomically at the database level.
Only one request gets `rowcount = 1`. The other gets `rowcount = 0` and
receives a 409 response immediately.

### SQL Injection Prevention
All queries use parameterized `?` placeholders — user input is never
interpolated directly into SQL strings.

### Transaction Atomicity
Registration involves two operations: decrementing seats and inserting a
registration record. Both are wrapped in a single transaction. If either
fails, `rollback()` undoes both — ensuring data is never left in a
partial state.

## Error Responses

| Status | Meaning |
|--------|---------|
| 201 | Resource created successfully |
| 200 | Request successful |
| 404 | Event or registration not found |
| 409 | Conflict (duplicate name, duplicate registration, event full) |
| 422 | Validation failed (past date, zero seats, bad format) |
| 500 | Internal server error |

## Testing
Run the included test script with the server running:

```bash
python test_api.py
```

Expected: 23/23 tests passing.