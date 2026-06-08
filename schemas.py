from pydantic import BaseModel, Field, field_validator
from datetime import datetime, time, timezone

class EventCreate(BaseModel):
    name: str = Field(..., min_length=1)
    total_seats: int
    event_date: str        # "2026-12-01"
    start_time: str        # "10:30"
    end_time: str          # "12:30"

    @field_validator("total_seats")
    @classmethod
    def seats_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Total seats must be greater than 0")
        return v

    @field_validator("event_date")
    @classmethod
    def date_must_be_future(cls, v: str):
        try:
            event_dt = datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("event_date must be in YYYY-MM-DD format e.g. 2026-12-01")
        if event_dt.date() <= datetime.now().date():
            raise ValueError("Event date must be in the future")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM 24hr format e.g. 10:30 or 14:00")
        return v

    @field_validator("end_time")
    @classmethod
    def end_must_be_after_start(cls, v: str, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class EventResponse(BaseModel):
    id: int
    name: str
    total_seats: int
    available_seats: int
    event_date: str
    start_time: str
    end_time: str
    created_at: str
    total_registrations: int = 0


class RegistrationCreate(BaseModel):
    user_name: str = Field(..., min_length=1)


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    user_name: str
    status: str
    registered_at: str