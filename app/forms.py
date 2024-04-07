from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, TextAreaField, DateTimeField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from .models import Service  # Pass på at denne importen matcher plasseringen av modellen din

from wtforms.validators import DataRequired, Length

class AddPatientForm(FlaskForm):
    first_name = StringField('Fornavn', validators=[DataRequired()])
    last_name = StringField('Etternavn', validators=[DataRequired()])
    personal_number = StringField('Personnummer', validators=[DataRequired(), Length(min=11, max=11)])
    birth_date = DateField('Fødselsdato', validators=[DataRequired()])
    gender = SelectField('Kjønn', choices=[('Mann', 'Mann'), ('Kvinne', 'Kvinne'), ('Annet', 'Annet')])
    address = StringField('Adresse', validators=[DataRequired()])
    postal_code = StringField('Postnummer', validators=[DataRequired()])
    municipality = StringField('Kommune', validators=[DataRequired()])
    submit = SubmitField('Legg til Pasient')

class EditPatientForm(FlaskForm):
    first_name = StringField('Fornavn', validators=[DataRequired()])
    last_name = StringField('Etternavn', validators=[DataRequired()])
    personal_number = StringField('Personnummer', validators=[DataRequired(), Length(min=11, max=11)])
    birth_date = DateField('Fødselsdato', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Kjønn', choices=[('Mann', 'Mann'), ('Kvinne', 'Kvinne'), ('Annet', 'Annet')], validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    postal_code = StringField('Postnummer', validators=[DataRequired()])
    municipality = StringField('Kommune', validators=[DataRequired()])
    submit = SubmitField('Oppdater Pasient')


class NewJournalEntryForm(FlaskForm):
    notes = TextAreaField('Notater', validators=[DataRequired()])
    submit_journal = SubmitField('Legg til Notat')

def available_services():
    return Service.query

class AppointmentForm(FlaskForm):
    service = QuerySelectField('Velg Tjeneste', query_factory=available_services, get_label='name', allow_blank=False)
    datetime = DateTimeField('Dato og tid', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    patient_id = SelectField('Pasient', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notater')
    submit = SubmitField('Lagre Avtale')

class ServiceForm(FlaskForm):
    name = StringField('Navn på Tjenesten', validators=[DataRequired()])
    duration = IntegerField('Varighet (i minutter)', validators=[DataRequired()])
    day_rate = FloatField('Dagtakst', validators=[DataRequired()])
    night_rate = FloatField('Kveldstakst', validators=[DataRequired()])
    submit = SubmitField('Legg Til Tjeneste')




