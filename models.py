# models.py
from datetime import datetime
from __init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# User model with roles for 'user' and 'provider'
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'provider'
    password_hash = db.Column(db.String(128), nullable=False)
    
    appointments = db.relationship('Appointment', backref='user', lazy=True, foreign_keys="Appointment.user_id")
    provided_appointments = db.relationship('Appointment', backref='provider', lazy=True, foreign_keys="Appointment.provider_id")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Appointment model to store booking information
class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(150), nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)
    appointment_desc = db.Column(db.Text, nullable=True)
    appointment_status = db.Column(db.String(20), default='pending')  # Options: 'pending', 'completed', 'canceled'
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Ensure unique constraint for a provider at the same time slot on the same day
    __table_args__ = (
        db.UniqueConstraint('provider_id', 'appointment_date', 'appointment_time', name='unique_appointment_per_provider'),
    )
