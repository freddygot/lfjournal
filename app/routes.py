from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from app.forms import RegistrationForm, LoginForm, PatientForm
from app.models import Psychologist, Patient

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
    form = PatientForm()
    if form.validate_on_submit():
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
    patients = Patient.query.filter_by(psychologist_id=current_user.id).all()
    return render_template('patients.html', title='My Patients', form=form, patients=patients)
