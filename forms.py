# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    phone = StringField('Phone', validators=[Length(min=10, max=15)])
    is_provider = BooleanField('Register as Provider')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AppointmentBookingForm(FlaskForm):
    provider_id = SelectField('Provider', choices=[], coerce=int, validators=[DataRequired()])
    appointment_type = SelectField('Appointment Type', choices=[('face', 'At the Hospital'), ('online', 'Online')], validators=[DataRequired()])
    appointment_desc = TextAreaField('Appointment Description', validators=[Length(max=200)])
    appointment_date = DateField('Appointment Date', format='%Y-%m-%d', validators=[DataRequired()])
    appointment_time = SelectField('Appointment Time', choices=[
        ('09:00', '09:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '01:00 PM'),
        ('14:00', '02:00 PM'),
        ('15:00', '03:00 PM'),
        ('16:00', '04:00 PM') ])     
    submit = SubmitField('Book Appointment')

class UpdateAppointmentStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')], validators=[DataRequired()])
    submit = SubmitField('Update Status')
