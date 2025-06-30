#!/usr/bin/env python3

import re
import os

from sqlalchemy import or_
from datetime import datetime
from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api

from models import *


@app.route('/')
def index():
    return '<h1>Project Server</h1>'


class Register(Resource):
    def post(self):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("E-Mail is required.")
        if not password:
            errors.append("Password is required.")

        if errors:
            return {'errors': errors}, 422
        
        try:
            new_planner = Planner(
                username=username,
                email=email
            )
            new_planner.password = password

            db.session.add(new_planner)
            db.session.commit()

            session['planner_id'] = new_planner.id

            return {
                'id': new_planner.id,
                'username': new_planner.username,
                'email': new_planner.email
            }, 201
        
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Username and e-mail must be unique.']}, 422
        
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Register Error: {exc}")
            return {'errors': ['An unexpected error occurred. Please try again.']}, 500
       

class Login(Resource):
    def post(self):
        try:
            username_or_email = request.form.get('username')  # Can be username or email
            password = request.form.get('password')
            
            planner = Planner.query.filter(
                or_(Planner.username == username_or_email, Planner.email == username_or_email)
            ).first()
            
            if planner and planner.check_password(password):
                session['planner_id'] = planner.id
                
                return {
                    'id': planner.id,
                    'username': planner.username,
                    'email': planner.email,
                }, 200
            else:
                return {'error': 'Invalid username, email or password'}, 401
            
        except Exception as exc:
            app.logger.error(f"Login Error: {exc}")
            return {'errors': ['An unexpected error occurred. Please try again.']}, 500


class CheckSession(Resource):
    def get(self):
        planner_id = session.get('planner_id')

        if planner_id:
            planner = db.session.get(Planner, planner_id)
            if planner:
                return {
                    'id': planner.id,
                    'username': planner.username,
                    'email' : planner.email
                }, 200
            else:
                return {'error': 'User not found'}, 401
        else:
            return {'error': 'Unauthorised'}, 401


class Profile(Resource):
    def get(self):
        planner_id = session.get('planner_id')

        if not planner_id:
            return {'error': 'Unauthorised. Please log in.'}, 401
        
        planner = db.session.get(Planner, planner_id)

        if not planner:
            return {'error': 'Planner not found.'}, 404
        
        return {
            'id': planner.id,
            'username': planner.username,
            'email': planner.email
        }, 200
  

class Events(Resource):
    def get(self):
        planner_id = session.get('planner_id')

        if not planner_id:
            return {'error': 'Unauthorised. Please log in.'}, 401
        
        events = Event.query.filter_by(planner_id=planner_id).all()

        return [
            {
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'venue': event.venue,
                'date': event.date.isoformat(),
                'time': event.time.isoformat() if event.time else None
            }
            for event in events
        ], 200
    
    def post(self):
        planner_id = session.get('planner_id')

        if not planner_id:
            return {'error': 'Unauthorised. Please log in.'}, 401
        
        data = request.form or request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        venue = data.get('venue')
        date_str = data.get('date')
        time_str = data.get('time')

        errors = []
        if not name:
            errors.append("Event name is required.")
        if not description:
            errors.append("Event descrption is required.")
        if not date_str:
            errors.append("Event date is required.")

        if errors:
            return {'errors': errors}, 422
        
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return {'error': 'Invalid date format.Use YYYY-MM-DD.'}, 422
        
        event_time = None
        if time_str:
            try:
                event_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                return {'error': 'Invalid time format. Use HH:MM (24hr).'}, 422
            
        new_event = Event(
            name=name,
            description=description,
            venue=venue,
            date=event_date,
            time=event_time,
            planner_id=planner_id
        )

        try:
            db.session.add(new_event)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Event with this name already exists.']}, 422
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Event Creation Error: {exc}")
            return {'errors': ['An unexpected error occurred. Please try again.']}, 500

        return {
            'id': new_event.id,
            'name': new_event.name,
            'description': new_event.description,
            'venue': new_event.venue,
            'date': new_event.date.isoformat(),
            'time': new_event.time.isoformat() if new_event.time else None
        }, 201


class Event(Resource):
    def get_planner_event_by_id(self, id):
        planner_id = session.get('planner_id')

        if not planner_id:
            return None, {'error': 'Unauthorised. Please log in.'}, 401
        
        event = Event.query.filter_by(id=id, planner_id=planner_id).first()

        if not event:
            return None, {'error': 'Event not found.'}, 404
        
        return event, None, None
        
    def get(self, id):
        event, error_response, status = self.get_planner_event_by_id(id)
        if error_response:
            return error_response, status
        
        return {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'venue': event.venue,
            'date': event.date.isoformat(),
            'time': event.time.isoformat() if event.time else None
        }, 200
    
    def patch(self, id):
        event, error_response, status = self.get_planner_event_by_id(id)
        if error_response:
            return error_response, status
        
        data = request.form or request.get_json()

        event.name = data.get('name', event.name)
        event.description = data.get('description', event.description)
        event.venue = data.get('venue', event.venue)
        
        if 'date' in data:
            try:
                event.date = datetime.strptime(data.get('date'), "%Y-%m-%d").date()
            except:
                return {'error': 'Invalid date format.Use YYYY-MM-DD.'}, 422
            
        if 'time' in data:
            try:
                event.time = datetime.strptime(data.get('time'), "%H:%M").time()
            except ValueError:
                return {'error': 'Invalid time format. Use HH:MM (24hr).'}, 422

        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Event Update Error: {exc}")
            return {'errors': ['An unexpected error occurred while updating this event.']}, 500

        return {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'venue': event.venue,
            'date': event.date.isoformat(),
            'time': event.time.isoformat() if event.time else None
        }, 200
    
    def delete(self, id):
        event, error_response, status = self.get_planner_event_by_id(id)
        if error_response:
            return error_response, status
        
        try:
            db.session.delete(event)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Delete Error: {exc}")
            return {'error': 'An unexpected error occurred while deleting this event.'}, 500

        return {'message': 'Event successfully deleted.'}, 200
    

class Guests(Resource):
    def get(self):
        planner_id = session.get('planner_id')

        if not planner_id:
            return {'error': 'Unauthorised. Please log in.'}, 401
        
        guests = Guest.query.filter_by(planner_id=planner_id).all()

        return [
            {
                'id': guest.id,
                "name": guest.name,
                "email": guest.email,
                "phone": guest.phone
            }
            for guest in guests
        ], 200
    
    def post(self):
        planner_id = session.get('planner_id')

        if not planner_id:
            return {'error': 'Unauthorised. Please log in.'}, 401
        
        data = request.form or request.get_json()

        name=data.get('name')
        email=data.get('email')
        phone=data.get('phone')

        errors = []
        if not name:
            errors.append("Guest's name is required.")
        if not email:
            errors.append("Guest's email address is required.")
        if not phone:
            errors.append("Guest's phone number is required.")
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format.")
        if phone and not re.match(r"^\+?\d{7,15}$", phone):
            errors.append("Invalid phone number format.")

        if errors:
            return {'errors': errors}, 422
        
        new_guest = Guest(
            name=name,
            email=email,
            phone=phone,
            planner_id=planner_id
        )

        try:
            db.session.add(new_guest)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Guest with this email already exists.']}, 422
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Guest Creation Error: {exc}")
            return {'errors': ['An unexpected error occurred. Please try again.']}, 500

        return{
            "id": new_guest.id,
            "name": new_guest.name,
            "email": new_guest.email,
            "phone": new_guest.phone
        }, 201


class Guest(Resource):
    def get_planner_guest_by_id(self, id):
        planner_id = session.get('planner_id')

        if not planner_id:
            return None, {'error': 'Unauthorised. Please log in.'}, 401
        
        guest = Guest.query.filter_by(id=id, planner_id=planner_id).first()

        if not guest:
            return None, {'error': 'Guest not found.'}, 404
        
        return guest, None, None
        
    def get(self, id):
        guest, error_response, status = self.get_planner_guest_by_id(id)
        if error_response:
            return error_response, status
        
        return {
            'id': guest.id,
            'name': guest.name,
            'email': guest.email,
            'phone': guest.phone
        }, 200
    
    def patch(self, id):
        guest, error_response, status = self.get_planner_guest_by_id(id)
        if error_response:
            return error_response, status
        
        data = request.form or request.get_json()

        errors=[]
        if 'email' in data and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors.append("Invalid email format.")
        if 'phone' in data and not re.match(r"^\+?\d{7,15}$", data['phone']):
            errors.append("Invalid phone number format.")

        if errors:
            return {'errors': errors}, 422
        
        guest.name = data.get('name', guest.name)
        guest.email = data.get('email', guest.email)
        guest.phone = data.get('phone', guest.phone)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['A guest with this email already exists.']}, 422
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Guest Update Error: {exc}")
            return {'errors': ['An unexpected error occurred while updating this guest.']}, 500

        return {
            'id': guest.id,
            'name': guest.name,
            'email': guest.email,
            'phone': guest.phone
        }, 200
    
    def delete(self, id):
        guest, error_response, status = self.get_planner_guest_by_id(id)
        if error_response:
            return error_response, status
        
        try:
            db.session.delete(guest)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Delete Error: {exc}")
            return {'error': 'An unexpected error occurred while deleting this guest.'}, 500

        return {'message': 'Guest successfully deleted.'}, 200
    

class EventGuests(Resource):
    def get(self, event_id):
        planner_id = session.get("planner_id")

        if not planner_id:
            return None, {'error': 'Unauthorised. Please log in.'}, 401
        
        event = Event.query.filter_by(id=event_id, planner_id=planner_id).first()
        if not event:
            return {'error': 'Event not found'}, 404
        
        guests = [
            {
                'id': attendance.guest.id,
                'name': attendance.guest.name,
                'email':attendance.guest.email,
                'phone':attendance.guest.phone,
            }
            for attendance in event.attendances
        ]

        return guests, 200
    

class Attendances(Resource):
    def post(self):
        planner_id = session.get('planner_id')

        if not planner_id:
            return {'error': 'Unauthorised. Please log in.'}, 401
        
        data = request.form or request.get_json()

        guest_id = data.get('guest_id')
        event_id = data.get('event_id')
        rsvp_status = data.get('rsvp_status', 'Pending')
        plus_ones = data.get('plus_ones', 0)

        if not guest_id or not event_id:
            return {"error": 'guest_id and event_id are required.'}, 422
        
        try:
            new_attendance = Attendance(
                guest_id=guest_id,
                event_id=event_id,
                planner_id=planner_id,
                rsvp_status=rsvp_status,
                plus_ones=plus_ones
            )

            db.session.add(new_attendance)
            db.session.commit()

            return {
                'id': new_attendance.id,
                'guest_id': new_attendance.guest_id,
                'event_id': new_attendance.event_id,
                'rsvp_status': new_attendance.rsvp_status,
                'plus_ones': new_attendance.plus_ones
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {'errors': ['This guest is already invited to this event.']}, 422   
        
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Attendance Creation Error: {exc}")
            return {'errors': ['An unexpected error occurred. Please try again.']}, 500
        

class Attendance(Resource):
    def attendance_by_event_guest(self, id):
        planner_id = session.get('planner_id')

        if not planner_id:
            return None, {'error': 'Unauthorised. Please log in.'}, 401
        
        attendance = Attendance.query.filter_by(id=id, planner_id=planner_id).first()
        if not attendance:
            return None, {'error': 'Attendance record not found.'}, 404
        
        return attendance, None, None
        
    def get(self, id):
        attendance, error_response, status = self.attendance_by_event_guest(id)
        if error_response:
            return error_response, status
        
        return {
            'id': attendance.id,
            'guest_id': attendance.guest_id,
            'guest_name': attendance.guest.name,
            'guest_email': attendance.guest.email,
            'event_id': attendance.event_id,
            'event_name': attendance.event.name,
            'rsvp_status': attendance.rsvp_status,
            'plus_ones': attendance.plus_ones
        }, 200
    
    def patch(self, id):
        attendance, error_response, status = self.attendance_by_event_guest(id)
        if error_response:
            return error_response, status
        
        data = request.form or request.get_json()

        if 'rsvp_status' in data:
            attendance.rsvp_status = data['rsvp_status']
        if 'plus_ones' in data:
            attendance.plus_ones = data['plus_ones']

        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Attendance Update Error: {exc}")
            return {'errors': ['An unexpected error occurred while updating this attendance.']}, 500

        return {
            'id': attendance.id,
            'guest_id': attendance.guest_id,
            'event_id': attendance.event_id,
            'rsvp_status': attendance.rsvp_status,
            'plus_ones': attendance.plus_ones
        }, 200
    
    def delete(self, id):
        attendance, error_response, status = self.attendance_by_event_guest(id)
        if error_response:
            return error_response, status
        
        try:
            db.session.delete(attendance)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error(f"Delete Error: {exc}")
            return {'error': 'An unexpected error occurred while deleting this attendance.'}, 500

        return {'message': 'Attendance (invitation) succesfully deleted.'}


class Logout(Resource):
    def delete(self):
        planner_id =  session.get('planner_id')

        if planner_id:
            session.pop('planner_id')
            return '', 204
        else:
            return {'error': 'Unauthorised'}, 401


api.add_resource(Register, '/register', endpoint='register')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Profile, '/profile', endpoint='profile')
api.add_resource(Events, '/events', endpoint='events')
api.add_resource(Event, '/events/<int:id>', endpoint='event')
api.add_resource(Guests, '/guests', endpoint='guests')
api.add_resource(Guest, '/guests/<int:id>', endpoint='guest')
api.add_resource(EventGuests, '/events/<int:event_id>/guests', endpoint='event_guests')
api.add_resource(Attendances, '/attendances', endpoint='attendances')
api.add_resource(Attendance, '/attendances/<int:id>', endpoint='attendance')
api.add_resource(Logout, '/logout', endpoint='logout')


if __name__ == '__main__':
    app.run( host='0.0.0.0', port=int(os.environ.get("PORT", 5555)), debug=True)