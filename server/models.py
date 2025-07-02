import re

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash

from config import db

class Planner(db.Model):
    __tablename__ = "planners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


    events = db.relationship("Event", backref="planner", cascade="all, delete-orphan")
    guests = db.relationship("Guest", backref="planner", cascade="all, delete-orphan")
    attendances = db.relationship("Attendance", backref="planner", cascade="all, delete-orphan")


    @property
    def password(self):
        raise AttributeError("Password cannot be viewed.")
    
    @password.setter
    def password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)
    
    def check_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)
    

    @validates("email")
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")
        return email
   

    def __repr__(self):
        return f"<User {self.id}: {self.username}, {self.email}>."
    

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
   


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    venue = db.Column(db.String)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)

    planner_id = db.Column(db.Integer, db.ForeignKey("planners.id"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


    attendances = db.relationship("Attendance", back_populates="event", cascade="all, delete-orphan")

    guests = association_proxy("attendances", "guest")


    def __repr__(self):
        return f"<Event {self.id}: {self.name}, {self.venue}. At {self.time}: {self.date}>."
    
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'venue': self.venue,
            'date': self.date.isoformat(),
            'time': self.time.isoformat() if self.time else None,
            'planner_id': self.planner_id,
            'guest_count': len(self.guests),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }



class Guest(db.Model):
    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)

    planner_id = db.Column(db.Integer, db.ForeignKey("planners.id"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


    attendances = db.relationship("Attendance", back_populates="guest", cascade="all, delete-orphan")

    events = association_proxy("attendances", "event")


    @validates("email")
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")
        return email

    @validates("phone")
    def validate_phone(self, key, phone):
        if not re.match(r"^\+?\d{7,15}$", phone):
            raise ValueError("Invalid phone number format.")
        return phone
    

    def __repr__(self):
        return f"<Guest {self.id}: {self.name}, {self.email}, {self.phone}>."
    

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }



class Attendance(db.Model):
    __tablename__ = "attendances"

    id = db.Column(db.Integer, primary_key=True)
    rsvp_status = db.Column(db.String, nullable=False)
    plus_ones = db.Column(db.Integer, nullable=False)

    guest_id = db.Column(db.Integer, db.ForeignKey("guests.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    planner_id = db.Column(db.Integer, db.ForeignKey("planners.id"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


    event = db.relationship("Event", back_populates="attendances")
    guest = db.relationship("Guest", back_populates="attendances")


    def __repr__(self):
        return f"<Attendance {self.id}: {self.guest.name}, {self.event_id}, {self.rsvp_status}, {self.plus_ones}>."
    

    def to_dict(self):
        return {
            'id': self.id,
            'rsvp_status': self.rsvp_status,
            'plus_ones': self.plus_ones,
            'guest_id': self.guest_id,
            'guest_name': self.guest.name,
            'event_id': self.event_id,
            'event_name': self.event.name,
            'planner_id': self.planner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }