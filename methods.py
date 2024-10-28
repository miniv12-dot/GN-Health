import os
from __init__ import *
from twilio.rest import Client
from models import *
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

# Load Twilio credentials from environment variables for security
account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'ACd5181f7223447675685712343aa79aba')
auth_token = os.getenv('TWILIO_AUTH_TOKEN', '[AuthToken]')
client = Client(account_sid, auth_token)

# Function to send SMS using Twilio
def send_sms(to, body):
    try:
        message = client.messages.create(
            messaging_service_sid='MG5c5e5a401612ba03df4cd3dfc7eeaa61',
            body=body,
            to=to
        )
        print(f'SMS sent: {message.sid}')
    except Exception as e:
        print(f'Failed to send SMS: {str(e)}')

# Function to simulate illness prediction
def get_illness_prediction(symptoms):
    # Simulated response for testing
    return {'predictions': ['Flu', 'Cold']}

# Function to generate time slots for appointments
def generate_time_slots():
    start_time = datetime.strptime('09:00', '%H:%M')
    end_time = datetime.strptime('17:00', '%H:%M')
    time_slots = []

    current_time = start_time
    while current_time <= end_time:
        time_slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(hours=1)

    return [(slot, slot) for slot in time_slots]  # return list of tuples for SelectField

# Function to seed providers if none exist
def seed_providers():
    # Check if a provider named David already exists to avoid duplicates
    existing_provider = User.query.filter_by(username="David").first()
    if existing_provider:
        print("Provider David already exists.")
    else:
        # Create a new provider with the username 'David' and password '123456'
        provider = User(username="David", role="provider")
        provider.set_password("123456")
        
        # Add and commit the new provider to the database
        db.session.add(provider)
        db.session.commit()
        print("Provider David seeded successfully.")