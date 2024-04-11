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

@app.route("/patient/<int:patient_id>")
@login_required
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.datetime.desc()).all()
    return render_template('patient_profile.html', patient=patient, appointments=appointments)

@app.route("/patient/edit/<int:patient_id>", methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        # Oppdater pasientinformasjon basert på form data
        patient.email = request.form['email']
        patient.phone_number = request.form['phone_number']
        # Oppdater flere felt basert på skjemaet
        db.session.commit()
        flash('Pasientinformasjon oppdatert', 'success')
        return redirect(url_for('view_patient', patient_id=patient.id))
    
    return render_template('edit_patient.html', patient=patient)

    
@app.route("/get_appointments")
@login_required
def get_appointments():
    appointments = Appointment.query.join(Patient, Appointment.patient_id == Patient.id).filter_by(psychologist_id=current_user.id).all()
    events = [
        {
            'id': appointment.id,
            'title': appointment.description,
            'start': appointment.datetime.isoformat(),
            'patientName': f"{appointment.patient.first_name} {appointment.patient.last_name}"
        } for appointment in appointments
    ]
    return jsonify(events)

@app.route("/get_appointment/<int:appointment_id>")
@login_required
def get_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        formatted_datetime = appointment.datetime.strftime('%Y-%m-%dT%H:%M')  # Formatert for datetime-local input
        return jsonify({
            'id': appointment.id,
            'datetime': formatted_datetime,
            'description': appointment.description,
            'patient_id': appointment.patient_id
        })
    else:
        return jsonify({'error': 'Appointment not found'}), 404




@app.route("/add_appointment", methods=['POST'])
def add_appointment():
    try:
        # Henter data som JSON
        data = request.get_json()
        datetime_str = data['datetime']
        description = data['description']
        patient_id = data['patient_id']
        
        # Formaterer datotid fra streng til datetime objekt
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')

        # Sjekker om pasienten finnes
        if patient_id:
            patient = Patient.query.get(patient_id)
            if not patient:
                return jsonify({"error": "Patient not found"}), 404
        
        # Oppretter ny avtale
        appointment = Appointment(datetime=datetime_obj, description=description, patient_id=patient_id)
        db.session.add(appointment)
        db.session.commit()

        return jsonify({"message": "Appointment added successfully", "appointment_id": appointment.id}), 200
    except ValueError as e:
        # Feil ved parsing av datotid
        return jsonify({"error": "Invalid datetime format", "details": str(e)}), 400
    except Exception as e:
        # Generisk serverfeil
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/update_appointment", methods=['POST'])
@login_required
def update_appointment():
    try:
        data = request.get_json()
        print("Mottatt data:", data)

        appointment_id = data.get('id')
        if not appointment_id:
            print("Mangler avtale ID")
            return jsonify({"error": "Missing appointment ID"}), 400

        print("Avtale ID:", appointment_id)
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        new_datetime_str = data.get('datetime')
        new_description = data.get('description')
        new_patient_id = data.get('patient_id')

        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'):
            try:
                appointment.datetime = datetime.strptime(new_datetime_str, fmt)
                break
            except ValueError:
                continue
        else:
            return jsonify({"error": "Invalid datetime format"}), 400

        appointment.description = new_description
        if new_patient_id:
            patient = Patient.query.get(new_patient_id)
            if not patient:
                return jsonify({"error": "Patient not found"}), 404
            appointment.patient_id = new_patient_id

        db.session.commit()
        return jsonify({"message": "Appointment updated successfully"}), 200
    except Exception as e:
        print("Feil under oppdatering av avtalen:", e)
        return jsonify({"error": "Internal server error"}), 500
