from fastapi import FastAPI, HTTPException, Query
from database import create_tables
from schemas import EventCreate, EventResponse, RegistrationCreate, RegistrationResponse
import crud

app = FastAPI(
    title="Event Registration System",
    description="Innovaxel Backend Assessment — Agha Ali Hassan",
    version="1.0.0"
)

# create tables on startup
@app.on_event("startup")
def startup():
    create_tables()


# ─── Events ───────────────────────────────────────────────

@app.get("/api/v1/events", response_model=list[EventResponse])
def get_events(
    upcoming_only: bool = Query(False, description="Show only future events"),
    sort_by_date: bool = Query(False, description="Sort events by date ascending")
):
    return crud.get_events(upcoming_only=upcoming_only, sort_by_date=sort_by_date)


@app.get("/api/v1/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int):
    event = crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/api/v1/events", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate):
    try:
        event = crud.create_event(
            name=payload.name,
            total_seats=payload.total_seats,
            event_date=payload.event_date,
            start_time=payload.start_time,
            end_time=payload.end_time
        )
        event["total_registrations"] = 0
        return event
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

# ─── Registrations ─────────────────────────────────────────

@app.post("/api/v1/events/{event_id}/register", response_model=RegistrationResponse, status_code=201)
def register_user(event_id: int, payload: RegistrationCreate):
    try:
        return crud.register_user(
            event_id=event_id,
            user_name=payload.user_name
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OverflowError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.delete("/api/v1/registrations/{registration_id}")
def cancel_registration(registration_id: int, user_name: str = Query(..., description="Name of the user cancelling")):
    try:
        return crud.cancel_registration(
            registration_id=registration_id,
            user_name=user_name
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Health Check ──────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Event Registration API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "docs": "http://127.0.0.1:8000/docs"
    }


# ─── Global Error Handler ──────────────────────────────────

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


