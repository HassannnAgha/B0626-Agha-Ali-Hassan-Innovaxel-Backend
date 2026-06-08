import requests

BASE = "http://127.0.0.1:8000/api/v1"

def log(test_name, response, expected_status):
    status = "✅ PASS" if response.status_code == expected_status else f"❌ FAIL (got {response.status_code})"
    print(f"{status} | {test_name}")
    if response.status_code != expected_status:
        print(f"       Response: {response.json()}")

print("\n========== EVENT TESTS ==========")

# 1. Create valid event
r = requests.post(f"{BASE}/events", json={
    "name": "Tech Conference",
    "total_seats": 2,
    "event_date": "2026-12-01",
    "start_time": "10:00",
    "end_time": "12:00"
})
log("Create valid event", r, 201)
event_id = r.json().get("id") if r.status_code == 201 else 1

# 2. Duplicate event name
r = requests.post(f"{BASE}/events", json={
    "name": "Tech Conference",
    "total_seats": 10,
    "event_date": "2026-12-02",
    "start_time": "10:00",
    "end_time": "12:00"
})
log("Duplicate event name → 409", r, 409)

# 3. Past date
r = requests.post(f"{BASE}/events", json={
    "name": "Old Event",
    "total_seats": 10,
    "event_date": "2024-01-01",
    "start_time": "10:00",
    "end_time": "12:00"
})
log("Past date → 422", r, 422)

# 4. Zero seats
r = requests.post(f"{BASE}/events", json={
    "name": "Zero Seat Event",
    "total_seats": 0,
    "event_date": "2026-12-03",
    "start_time": "10:00",
    "end_time": "12:00"
})
log("Zero seats → 422", r, 422)

# 5. Negative seats
r = requests.post(f"{BASE}/events", json={
    "name": "Negative Event",
    "total_seats": -5,
    "event_date": "2026-12-03",
    "start_time": "10:00",
    "end_time": "12:00"
})
log("Negative seats → 422", r, 422)

# 6. Invalid time format
r = requests.post(f"{BASE}/events", json={
    "name": "Bad Time Event",
    "total_seats": 10,
    "event_date": "2026-12-03",
    "start_time": "25:99",
    "end_time": "12:00"
})
log("Invalid time format → 422", r, 422)

# 7. End time before start time
r = requests.post(f"{BASE}/events", json={
    "name": "Bad Time Event 2",
    "total_seats": 10,
    "event_date": "2026-12-03",
    "start_time": "14:00",
    "end_time": "10:00"
})
log("End before start → 422", r, 422)

# 8. Get all events
r = requests.get(f"{BASE}/events")
log("Get all events → 200", r, 200)

# 9. Get upcoming only
r = requests.get(f"{BASE}/events?upcoming_only=true")
log("Get upcoming events → 200", r, 200)

# 10. Get sorted by date
r = requests.get(f"{BASE}/events?sort_by_date=true")
log("Get sorted by date → 200", r, 200)

# 11. Get single event
r = requests.get(f"{BASE}/events/{event_id}")
log("Get single event → 200", r, 200)

# 12. Get non-existent event
r = requests.get(f"{BASE}/events/9999")
log("Get non-existent event → 404", r, 404)

print("\n========== REGISTRATION TESTS ==========")

# 13. Register user
r = requests.post(f"{BASE}/events/{event_id}/register", json={"user_name": "Hassan"})
log("Register user → 201", r, 201)
reg_id = r.json().get("id") if r.status_code == 201 else 1

# 14. Register same user again
r = requests.post(f"{BASE}/events/{event_id}/register", json={"user_name": "Hassan"})
log("Duplicate registration → 409", r, 409)

# 15. Register second user (event has 2 seats)
r = requests.post(f"{BASE}/events/{event_id}/register", json={"user_name": "Hamza"})
log("Register second user → 201", r, 201)

# 16. Register third user — event full (only 2 seats)
r = requests.post(f"{BASE}/events/{event_id}/register", json={"user_name": "Emaan"})
log("Event full → 409", r, 409)

# 17. Register on non-existent event
r = requests.post(f"{BASE}/events/9999/register", json={"user_name": "Hassan"})
log("Register on non-existent event → 404", r, 404)

# 18. Empty username
r = requests.post(f"{BASE}/events/{event_id}/register", json={"user_name": ""})
log("Empty username → 422", r, 422)

print("\n========== CANCELLATION TESTS ==========")

# 19. Cancel registration
r = requests.delete(f"{BASE}/registrations/{reg_id}?user_name=Hassan")
log("Cancel registration → 200", r, 200)

# 20. Verify seat came back — available_seats should be 1 again
r = requests.get(f"{BASE}/events/{event_id}")
available = r.json().get("available_seats")
passed = available == 1
print(f"{'✅ PASS' if passed else '❌ FAIL'} | Seat restored after cancel (available={available})")

# 21. Cancel already cancelled
r = requests.delete(f"{BASE}/registrations/{reg_id}?user_name=Hassan")
log("Cancel already cancelled → 404", r, 404)

# 22. Cancel with wrong username
r = requests.delete(f"{BASE}/registrations/2?user_name=WrongName")
log("Cancel with wrong username → 404", r, 404)

# 23. Cancel non-existent registration
r = requests.delete(f"{BASE}/registrations/9999?user_name=Hassan")
log("Cancel non-existent → 404", r, 404)

print("\n========== DONE ==========\n")