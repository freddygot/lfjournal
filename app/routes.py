from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from app import app, db
from app.forms import RegistrationForm, LoginForm, PatientForm
from app.models import Psychologist, Patient, Appointment

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Psychologist(email=form.email.data)
        user.set_password(form.password.data)  # Oppdater denne linjen
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Psychologist.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/patients", methods=['GET', 'POST'])
@login_required
def patients():
    print("Metode: ", request.method)  # Debugging: Sjekk HTTP-metoden
    form = PatientForm()
    if form.validate_on_submit():
        print("Formen er validert")  # Debugging: Sjekk om formen passerer validering
        patient = Patient(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birth_number=form.birth_number.data,
            birth_date=form.birth_date.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            gender=form.gender.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            municipality=form.municipality.data,
            psychologist_id=current_user.id
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient has been registered!', 'success')
        return redirect(url_for('patients'))
    else:
        print(form.errors)  # Skriver ut valideringsfeilene
    patients = Patient.query.filter_by(psychologist_id=current_user.id).all()
    return render_template('patients.html', title='My Patients', form=form, patients=patients)

@app.route("/get_patients")
@login_required
def get_patients():
    # Anta at hver psykolog har sine egne pasienter, og vi henter bare pasienter for den innloggede psykologen
    patients = Patient.query.filter_by(psychologist_id=current_user.id).all()
    patient_list = [
        {"id": patient.id, "full_name": patient.first_name + " " + patient.last_name}
        for patient in patients
    ]
    return jsonify(patient_list)

    
@app.route("/get_appointments")
def get_appointments():
    appointments = Appointment.query.all()
    events = []
    for appointment in appointments:
        events.append({
            'title': appointment.description,
            'start': appointment.datetime.isoformat(),
            # Legg til flere felt som 'end' hvis nødvendig
        })
    return jsonify(events)

@app.route("/add_appointment", methods=['POST'])
def add_appointment():
    try:
        datetime_str = request.form['datetime']
        description = request.form['description']
        patient_id = request.form.get('patient_id')
        
        # Prøv forskjellige datotidsformater
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'):
            try:
                datetime_obj = datetime.strptime(datetime_str, fmt)
                break
            except ValueError:
                pass
        else:
            # Ingen av formatene matchet
            return jsonify({"error": "Invalid datetime format"}), 400

        if patient_id:
            patient = Patient.query.get(patient_id)
            if not patient:
                return jsonify({"error": "Patient not found"}), 404
        
        appointment = Appointment(datetime=datetime_obj, description=description, patient_id=patient_id)
        db.session.add(appointment)
        db.session.commit()
        return jsonify({"message": "Appointment added successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

   