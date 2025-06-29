#!/usr/bin/env 

from datetime import datetime

from config import app, db

from models import Planner, Event, Guest, Attendance

with app.app_context():
    db.session.query(Event).delete()
    db.session.query(Guest).delete()
    db.session.query(Attendance).delete()
    print("Existing data cleared successfully!")
    db.session.commit()

    planner = Planner.query.filter_by(email="test@planner.com").first()
    if planner:
        db.session.delete(planner)
        db.session.commit()

    planner = Planner(
        username="test_planner",
        email="test@planner.com",
        password="test-password123"
    )
    db.session.add(planner)
    db.session.commit()


    event = Event(
        name="Sample Event",
        description="This is a sample event for testing.",
        venue="Test Venue",
        date=datetime(2025, 7, 1).date(),
        time=datetime(2025, 7, 1, 14, 0).time(),
        planner_id=planner.id
    )

    db.session.add(event)
    db.session.commit()

    guest = Guest(
        name="Sample Guest",
        email="guest@example.com",
        phone="1234567890",
        planner_id=planner.id
    )

    db.session.add(guest)
    db.session.commit()

    attendance = Attendance(
        rsvp_status="Accepted",
        plus_ones=0,
        guest_id=guest.id,
        event_id=event.id,
        planner_id=planner.id
    )

    db.session.add(attendance)
    db.session.commit()

    print("Seed data added successfully!")