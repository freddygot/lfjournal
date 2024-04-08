from flask_login import UserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return Psychologist.query.get(int(user_id))

class Psychologist(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    title = db.Column(db.String(50), nullable=True)  # Psychologist, Specialist, or Student
    clinic = db.Column(db.String(100), nullable=True)
    birth_number = db.Column(db.String(11), unique=True, nullable=True)  # Norwegian National Identity Number
    address = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(128))  # Legg til dette feltet
    gender = db.Column(db.String(10), nullable=True)
    patients = db.relationship('Patient', backref='psychologist', lazy=True)

# Metode for å sette passordet (lagrer en hash istedenfor klartekst)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Metode for å sjekke passordet
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_number = db.Column(db.String(11), unique=True, nullable=False)
    birth_date = db.Column(db.String(10), nullable=False)  # or db.Date for actual date objects
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    municipality = db.Column(db.String(50), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('psychologist.id'), nullable=False)
