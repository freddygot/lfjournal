from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class RegistrationForm(FlaskForm):
    # Felt for registrering
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    # Felt for innlogging
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PatientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    birth_number = StringField('Birth Number', validators=[DataRequired(), Length(min=11, max=11)])
    birth_date = StringField('Birth Date', validators=[DataRequired()])  # Consider using DateField for actual projects
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    municipality = StringField('Municipality', validators=[DataRequired()])
    submit = SubmitField('Register Patient')
