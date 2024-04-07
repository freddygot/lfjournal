from . import db
from datetime import datetime

class Psychologist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    personal_number = db.Column(db.String(11), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    municipality = db.Column(db.String(100), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('psychologist.id'), nullable=False)
    psychologist = db.relationship('Psychologist', backref=db.backref('patients', lazy='dynamic'))

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=False)
    appointment = db.relationship('Appointment', backref=db.backref('journal_entries', lazy=True))
    

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # Legg til dette feltet
    notes = db.Column(db.Text)  # Valgfritt, hvis du vil ha notater direkte på avtalen
    patient = db.relationship('Patient', backref='appointments')
    service = db.relationship('Service', backref='appointments')  # Legg til denne relasjonen

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Varighet i minutter
    day_rate = db.Column(db.Float, nullable=False)  # Pris mellom 0700-1600
    night_rate = db.Column(db.Float, nullable=False)  # Pris mellom 1600-0700