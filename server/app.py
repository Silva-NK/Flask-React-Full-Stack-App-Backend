#!/usr/bin/env python3

import re
import os

from sqlalchemy import or_
from flask import request, session
from flask_restful import Resource
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from config import db, app, api

from models import *


@app.route('/')
def index():
    return '<h1>Project Server</h1>'


class Register(Resource):
    def post(self):
        data = request.get_json()

        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm = data.get('confirm_password')

        if not all([name, username, email, password, confirm]):
            return {"error": "All fields are required."}, 400
        
        if password != confirm:
            return {"error": "Passwords do not match."}, 400
        
        if Planner.query.filter_by(username=username).first():
            return {"error": "This username already exists."}, 400
        
        if Planner.query.filter_by(email=email).first():
            return {"error": "This email is already registered."}, 400
        
        try:
            new_user = Planner(
                name=name,
                username=username,
                email=email
            )
            new_user.password = password

            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)

            session['user_id'] = new_user.id

            return {
                "message": "User registered successfully.",
                "user": new_user.to_dict()
            }, 201
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class Login(Resource):
    def post(self):
        try:
            data = request.get_json()

            username_or_email = data.get('username')  # Can be username or email
            password = data.get('password')

            if not all([username_or_email, password]):
                return {"error": "Username/email and password are required."}, 400
            
            user = Planner.query.filter(
                or_(Planner.username == username_or_email, Planner.email == username_or_email)
            ).first()
            
            if not user or not user.check_password(password):
                return {"error": "Invalid username/email and password."}, 401
                
            session['user_id'] = user.id
                
            return {
                    "message": "Login successful.",
                    "user": user.to_dict()
            }, 200
               
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised.Please log in."}, 401

        user = db.session.get(Planner, user_id)
        if not user:
            return {"error": "User not found."}, 404
            
        return {
            "message": "User is logged in.",
            "user": user.to_dict()
        }, 200


class Profile(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        user = db.session.get(Planner, user_id)
        if not user:
            return {"error": "User not found."}, 404
        
        today = date.today()
        past_events = [event for event in user.events if event.date < today]
        upcoming_events = [event for event in user.events if event.date >= today]
        
        return {
            "message": "User profile retrieved successfully.",
            "profile": user.to_dict(),
            "event_count": len(user.events),
            "guest_count": len(user.guests),
            "past_event_count": len(past_events),
            "upcoming_event_count": len(upcoming_events)
        }, 200


class Events(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        try:
            events = db.session.query(Event).filter_by(planner_id=user_id).all()
            return [event.to_dict() for event in events],200
        except Exception as exc:
            return {"error": str(exc)}, 500
    
    def post(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        venue = data.get('venue')
        date_str = data.get('date')
        time_str = data.get('time')

        if not all([name, description, date_str]):
            return {"error": "Name, description and date are required."}, 400
        
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
        
        event_time = None
        if time_str:
            try:
                event_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                return {"error": "Invalid time format. Use HH:MM (24hr)."}, 400
            
        try:
            new_event = Event(
                name=name,
                description=description,
                venue=venue,
                date=event_date,
                time=event_time,
                planner_id=user_id
            )

            db.session.add(new_event)
            db.session.commit()
            db.session.refresh(new_event)

            return {
                "message": "Event created successfully.",
                "event": new_event.to_dict()
            }, 201
            
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error."}, 400
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class EventByID(Resource):  
    def get(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        event = db.session.get(Event, id)
        if not event or event.planner_id != user_id:
            return {"error": "Event not found."}, 404
        
        return event.to_dict(), 200
    
    def patch(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        event = db.session.get(Event, id)
        if not event or event.planner_id != user_id:
            return {"error": "Event not found."}, 404
        
        data = request.get_json()

        name = data.get('name')
        description = data.get('description')
        venue = data.get('venue')
        date_str = data.get('date')
        time_str = data.get('time')

        if name:
            event.name = name
        if description:
            event.description = description
        if venue:
            event.venue = venue
        if date_str:
            try:
                event.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
        if time_str:
            try:
                event.time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                return {"error": "Invalid time format. Use HH:MM (24hr)."}, 400
            
        try:
            db.session.commit()
            db.session.refresh(event)

            return {
                "message": "Event updated successfully.",
                "event": event.to_dict()
            }, 200
        
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error."}, 400
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500

    
    def delete(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        event = db.session.get(Event, id)
        if not event or event.planner_id != user_id:
            return {"error": "Event not found."}, 404
        
        try:
            db.session.delete(event)
            db.session.commit()
            return {"message": "Event deleted successfully."}, 200
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500
    

class Guests(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        try:
            guests = db.session.query(Guest).filter_by(planner_id=user_id).all()
            return [guest.to_dict() for guest in guests], 200
        except Exception as exc:
            return {"error": str(exc)}, 500
    
    def post(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        data = request.get_json()

        name=data.get('name')
        email=data.get('email')
        phone=data.get('phone')

        if not all([name, email, phone]):
            return {"error": "Name, email and phone are required."}, 400
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"error": "Invalid email format."}, 400
        
        if not re.match(r"^\+?\d{7,15}$", phone):
            return {"error":"Invalid phone number format."}, 400


        try:
            new_guest = Guest(
                name=name,
                email=email,
                phone=phone,
                planner_id=user_id
        )
            db.session.add(new_guest)
            db.session.commit()
            db.session.refresh(new_guest)

            return {
                "message": "Guest added succesfully.",
                "guest": new_guest.to_dict()
        }, 201

        except IntegrityError:
            db.session.rollback()
            return {'errors': 'Guest with this email already exists.'}, 400
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500
        

class GuestByID(Resource):
    def get(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        guest = db.session.get(Guest, id)
        if not guest or guest.planner_id != user_id:
            return {"error": "Guest not found."}, 404
        
        return guest.to_dict(), 200
    
    def patch(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        guest = db.session.get(Guest, id)
        if not guest or guest.planner_id != user_id:
            return {"error": "Guest not found."}, 404
        
        data = request.get_json()
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')

        if name:
            guest.name = name

        if email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return {"error": "Invalid email format."}, 400
            guest.email = email

        if phone:
            if not re.match(r"^\+?\d{7,15}$", phone):
                return {"error":"Invalid phone number format."}, 400
            guest.phone = phone

        try:
            db.session.commit()
            db.session.refresh(guest)

            return {
                "message": "Guest updated succesfully.",
                "guest": guest.to_dict()
            }, 200

        except IntegrityError:
            db.session.rollback()
            return {'errors': ['A guest with this email already exists.']}, 400
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500
    
    def delete(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        guest = db.session.get(Guest, id)
        if not guest or guest.planner_id != user_id:
            return {"error": "Guest not found."}, 404
        
        try:
            db.session.delete(guest)
            db.session.commit()
            return {'message': 'Guest deleted successfully.'}, 200
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500 
  

class Attendances(Resource):
    def post(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        data = request.get_json()

        guest_id = data.get('guest_id')
        event_id = data.get('event_id')

        if not all([guest_id, event_id]):
            return {"error": "guest_id and event_id are required."}, 400
        
        guest = db.session.get(Guest, guest_id)
        event = db.session.get(Event, event_id)

        if not guest or guest.planner_id != user_id:
            return {"error": "Guest not found or unauthorised."}, 404
        
        if not event or event.planner_id != user_id:
            return {"error": "Event not found or unauthorised."}, 404
        
        existing_attendance = db.session.query(Attendance).filter_by(
            guest_id=guest_id,
            event_id=event_id,
            planner_id=user_id
        ).first()

        if existing_attendance:
            return {"error": "This guest is already invited to this event."}, 400
        
        try:
            attendance = Attendance(
                guest_id=guest_id,
                event_id=event_id,
                rsvp_status="Pending",
                plus_ones=0,
                planner_id=user_id,
            )

            db.session.add(attendance)
            db.session.commit()
            db.session.refresh(attendance)

            return {
                "message": "Attendance created successfully.",
                "attendance": attendance.to_dict()
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error."}, 400
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500
        

class AttendanceByID(Resource):
    def get(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        attendance = db.session.get(Attendance, id)
        if not attendance or attendance.planner_id != user_id:
            return {"error": "Attendance not found."}, 404
        
        return attendance.to_dict(), 200
    
    def patch(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        attendance = db.session.get(Attendance, id)
        if not attendance or attendance.planner_id != user_id:
            return {"error": "Attendance not found."}, 404
        
        data = request.get_json()

        rsvp_status = data.get('rsvp_status')
        plus_ones =  data.get('plus_ones')

        if rsvp_status:
            attendance.rsvp_status = rsvp_status

        if plus_ones is not None:
            if not isinstance(plus_ones, int) or plus_ones < 0:
                return {"error": "plus_ones must be a numeric value."}, 400
            
            attendance.plus_ones = plus_ones

        try:
            db.session.commit()
            db.session.refresh(attendance)

            return {
                "message": "Attendance updated successfully.",
                "attendance": attendance.to_dict()
            }, 200

        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error."}, 400
        
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500
    
    def delete(self, id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401

        attendance = db.session.get(Attendance, id)
        if not attendance or attendance.planner_id != user_id:
            return {"error": "Attendance not found."}, 404
        
        try:
            db.session.delete(attendance)
            db.session.commit()
            return {'message': 'Attendance deleted successfully.'}, 200

        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500

class EventGuests(Resource):
    def get(self, event_id):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorised. Please log in."}, 401
        
        event = db.session.get(Event, event_id)
        if not event or event.planner_id != user_id:
            return {"error": "Event not found."}, 404
        
        include_rsvp = request.args.get("include_rsvp", "false").lower == 'true'
        
        attendances = db.session.query(Attendance).filter_by(
            event_id=event_id,
            planner_id=user_id
        ).all()

        event_guests = []
        for attendance in attendances:
            guest_data = attendance.guest.to_dict()
            if include_rsvp:
                guest_data['rsvp_status'] = attendance.rsvp_status
                guest_data['plus_ones'] = attendance.plus_ones
            
            event_guests.append(guest_data)

        return event_guests, 200


class Logout(Resource):
    def post(self):
        user_id =  session.get('user_id')

        if user_id:
            session.pop('user_id')
            return {"message": "Logged out successfully."}, 200
        else:
            return {"error": "No active session."}, 400


api.add_resource(Register, '/register', endpoint='register')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Profile, '/profile', endpoint='profile')
api.add_resource(Events, '/events', endpoint='events')
api.add_resource(EventByID, '/events/<int:id>', endpoint='event')
api.add_resource(Guests, '/guests', endpoint='guests')
api.add_resource(GuestByID, '/guests/<int:id>', endpoint='guest')
api.add_resource(Attendances, '/attendances', endpoint='attendances')
api.add_resource(AttendanceByID, '/attendances/<int:id>', endpoint='attendance')
api.add_resource(EventGuests, '/events/<int:event_id>/guests', endpoint='event_guests')
api.add_resource(Logout, '/logout', endpoint='logout')


# if __name__ == '__main__':
#     app.run( host='0.0.0.0', port=int(os.environ.get("PORT", 5555)), debug=True)
if __name__ == '__main__':
    app.run(host="localhost", port=5555, debug=True)