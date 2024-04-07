from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Psychologist  # Endret fra User til Psychologist
from .forms import AddPatientForm, EditPatientForm, NewJournalEntryForm, AppointmentForm, ServiceForm
from .models import Patient, Appointment, Service  
from flask import current_app as app
from datetime import datetime
from .models import JournalEntry

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        birth_date = request.form.get('birth_date')
        password = request.form.get('password')

        if not email:
            flash('E-post er påkrevd.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        # Sjekker om e-posten allerede finnes i databasen
        psychologist = Psychologist.query.filter_by(email=email).first()  # Endret fra user til psychologist
        if psychologist:
            flash('En bruker med denne e-postadressen finnes allerede.')
            return redirect(url_for('register'))

        new_psychologist = Psychologist(first_name=first_name, last_name=last_name, email=email,
                        phone_number=phone_number, birth_date=datetime.strptime(birth_date, '%Y-%m-%d').date(),
                        password=hashed_password)
        db.session.add(new_psychologist)
        db.session.commit()

        flash('Registrering vellykket. Du kan nå logge inn.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'psychologist_id' not in session:  # Endret fra user_id til psychologist_id
        flash('Vennligst logg inn for å tilgang denne siden.')
        return redirect(url_for('login'))

    psychologist_id = session['psychologist_id']  # Endret fra user_id til psychologist_id
    psychologist = Psychologist.query.get(psychologist_id)  # Endret fra user til psychologist

    if request.method == 'POST':
        psychologist.first_name = request.form['first_name']
        psychologist.last_name = request.form['last_name']
        psychologist.email = request.form['email']
        psychologist.phone_number = request.form['phone_number']
        psychologist.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()

        db.session.commit()
        flash('Profilen din har blitt oppdatert.')
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', psychologist=psychologist)  # Endret fra user til psychologist

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email:
            flash('E-post er påkrevd.')
            return redirect(url_for('login'))

        psychologist = Psychologist.query.filter_by(email=email).first()  # Endret fra user til psychologist

        if psychologist and check_password_hash(psychologist.password, password):
            session['psychologist_id'] = psychologist.id  # Endret fra user_id til psychologist_id
            session['email'] = psychologist.email  # Oppdaterer session til å inneholde brukerens (psykologens) e-post
            flash('Du er nå logget inn.')
            return redirect(url_for('dashboard'))
        else:
            flash('Innlogging mislyktes. Sjekk din e-post og passord.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('psychologist_id', None)  # Endret fra user_id til psychologist_id
    session.pop('email', None)  # Husk å fjerne e-posten fra økten også
    flash('Du er nå logget ut.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'psychologist_id' not in session:
        flash('Vennligst logg inn for å se denne siden.')
        return redirect(url_for('login'))

    psychologist_id = session.get('psychologist_id')
    psychologist = Psychologist.query.get(psychologist_id)

    if psychologist is None:
        flash('Brukeren ble ikke funnet. Vennligst logg inn på nytt.')
        return redirect(url_for('login'))

    appointments = Appointment.query.join(Patient, Appointment.patient_id == Patient.id)\
                                     .filter(Patient.psychologist_id == psychologist_id)\
                                     .filter(Appointment.start_datetime >= datetime.utcnow())\
                                     .order_by(Appointment.start_datetime).all()

    services = Service.query.all()  # Hent alle tjenester

    return render_template('dashboard.html', psychologist=psychologist, appointments=appointments, services=services)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    form = AddPatientForm()
    if form.validate_on_submit():
        existing_patient = Patient.query.filter_by(personal_number=form.personal_number.data).first()
        if existing_patient:
            flash('En pasient med dette personnummeret finnes allerede.')
            return redirect(url_for('add_patient'))

        new_patient = Patient(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            personal_number=form.personal_number.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            municipality=form.municipality.data,
            psychologist_id=session['psychologist_id']
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('Pasient lagt til.')
        return redirect(url_for('dashboard'))
    return render_template('add_patient.html', form=form)

@app.route('/my_patients')
def my_patients():
    if 'psychologist_id' not in session:
        flash('Vennligst logg inn for å se denne siden.')
        return redirect(url_for('login'))

    psychologist_id = session.get('psychologist_id')
    psychologist = Psychologist.query.get(psychologist_id)
    if psychologist:
        patients = psychologist.patients.all()
        return render_template('my_patients.html', patients=patients)
    else:
        flash('Psykiatrisk ID ikke funnet.')
        return redirect(url_for('dashboard'))
    
@app.route('/patient/<int:patient_id>', methods=['GET', 'POST'])
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    edit_form = EditPatientForm(obj=patient)  # Forutsetter at dette skjemaet er korrekt satt opp
    journal_form = NewJournalEntryForm()  # Anta dette skjemaet er korrekt satt opp for nye journalnotater

    if request.method == 'POST' and 'submit' in request.form:
        if edit_form.validate_on_submit():
            edit_form.populate_obj(patient)
            db.session.commit()
            flash('Pasientinformasjon oppdatert.')
            return redirect(url_for('view_patient', patient_id=patient_id))

    if request.method == 'POST' and 'submit_journal' in request.form:
        if journal_form.validate_on_submit():
            # Denne delen antar at du har rettet tidligere nevnte feil ved å bruke appointment_id korrekt
            new_journal_entry = JournalEntry(appointment_id=appointment_id, notes=journal_form.notes.data)
            db.session.add(new_journal_entry)
            db.session.commit()
            flash('Journalnotat lagt til.')
            return redirect(url_for('view_patient', patient_id=patient_id))

    # Hent alle journalnotater knyttet til denne pasienten gjennom avtaler
    journal_entries = JournalEntry.query.join(Appointment).join(Patient)\
        .filter(Patient.id == patient_id).order_by(JournalEntry.entry_date.desc()).all()

    return render_template('view_patient.html', patient=patient, edit_form=edit_form, 
                           journal_form=journal_form, journal_entries=journal_entries)


@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    # Parse skjemadata
    appointment_date_str = request.form.get('appointment_date')
    start_time_str = request.form.get('appointment_start_time')
    service_id = request.form.get('service')  # ID for valgt tjeneste
    patient_id = request.form.get('patient_id')
    notes = request.form.get('notes')

    # Konverterer dato og start-tid-streng til datetime-objekter
    start_datetime = datetime.strptime(f"{appointment_date_str} {start_time_str}", '%Y-%m-%d %H:%M')

    # Finn valgt tjeneste og beregn sluttid basert på tjenestens varighet
    selected_service = Service.query.get(service_id)
    if selected_service:
        service_duration = selected_service.duration
        end_datetime = start_datetime + timedelta(minutes=service_duration)
    else:
        # Hvis ingen tjeneste er valgt, eller tjenesten ikke finnes, bruker manuell sluttid hvis tilgjengelig
        end_time_str = request.form.get('appointment_end_time')
        if end_time_str:
            end_datetime = datetime.strptime(f"{appointment_date_str} {end_time_str}", '%Y-%m-%d %H:%M')
        else:
            flash('Ingen gyldig tjeneste valgt og ingen sluttid spesifisert.')
            return redirect(url_for('add_appointment'))

    # Opprett og lagre den nye avtalen
    new_appointment = Appointment(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        patient_id=patient_id,
        notes=notes,
        service_id=selected_service.id if selected_service else None  # Lagre ID for valgt tjeneste
    )
    db.session.add(new_appointment)
    db.session.commit()

    flash('Ny avtale lagt til.')
    return redirect(url_for('dashboard'))
@app.route('/appointment/<int:appointment_id>')
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    # Anta at du har en HTML-mal kalt 'view_appointment.html' for å vise detaljer om avtalen
    return render_template('view_appointment.html', appointment=appointment)

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    # Finn avtalen som skal slettes basert på `appointment_id`
    appointment = Appointment.query.get_or_404(appointment_id)

    # Slett først alle tilknyttede journalnotater
    for entry in appointment.journal_entries:
        db.session.delete(entry)

    # Deretter slett selve avtalen
    db.session.delete(appointment)
    db.session.commit()

    flash('Avtalen og alle tilknyttede journalnotater ble slettet.')
    return redirect(url_for('dashboard'))


@app.route('/add_journal_entry/<int:appointment_id>', methods=['POST'])
def add_journal_entry(appointment_id):
    if 'psychologist_id' not in session:
        flash('Vennligst logg inn for å utføre denne handlingen.')
        return redirect(url_for('login'))
    
    journal_notes = request.form.get('journal_notes')
    if journal_notes:
        new_entry = JournalEntry(appointment_id=appointment_id, notes=journal_notes, entry_date=datetime.utcnow())
        db.session.add(new_entry)
        db.session.commit()
        flash('Journalnotat lagt til.')
    else:
        flash('Notatet kan ikke være tomt.')

    return redirect(url_for('view_appointment', appointment_id=appointment_id))

@app.route('/add-service', methods=['GET', 'POST'])
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(name=form.name.data, duration=form.duration.data,
                          day_rate=form.day_rate.data, night_rate=form.night_rate.data)
        db.session.add(service)
        db.session.commit()
        flash('Ny tjeneste er lagt til.')
        return redirect(url_for('add_service'))
    return render_template('add_service.html', form=form)
