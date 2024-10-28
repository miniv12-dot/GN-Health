# app.py
from flask import *
from __init__ import *
from datetime import datetime
from methods import send_sms, seed_providers
from forms import *
from models import User, Appointment

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

#----------------- Unified Authentication -----------------#

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        role = 'provider' if form.is_provider.data else 'user'
        user = User(username=form.username.data, phone=form.phone.data, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'provider':
                return redirect(url_for('provider_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

#----------------- User Usecases -----------------#

@app.route('/patientbooking', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'user':
        flash('Access denied. Providers cannot book appointments.', 'danger')
        return redirect(url_for('index'))

    providers = User.query.filter_by(role='provider').all()
    form = AppointmentBookingForm()
    form.provider_id.choices = [(provider.id, provider.username) for provider in providers]

    if form.validate_on_submit():
        # Check if the provider is already booked at the selected date and time
        existing_appointment = Appointment.query.filter_by(
            provider_id=form.provider_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data
        ).first()

        if existing_appointment:
            flash("The provider is already booked for the selected time.", "danger")
            return redirect(url_for('book_appointment'))

        # Convert the appointment_time from string to datetime.time
        appointment_time = datetime.strptime(form.appointment_time.data, '%H:%M').time()

        new_appointment = Appointment(
            patient_name=current_user.username,
            user_id=current_user.id,
            provider_id=form.provider_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=appointment_time,
            appointment_type=form.appointment_type.data,
            appointment_desc=form.appointment_desc.data,
            appointment_status='pending',
            date_created=datetime.utcnow()
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        send_sms('+1234567890', f'New appointment booked for {current_user.username} on {form.appointment_date.data} at {form.appointment_time.data}.')
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('my_appointments'))

    return render_template('user/patientbooking.html', form=form)


@app.route('/my_appointments')
@login_required
def my_appointments():
    if current_user.role != 'user':
        flash('Access denied. Only users can view appointments.', 'danger')
        return redirect(url_for('index'))
    
    appointments = (
        db.session.query(Appointment, User.username.label("provider_name"))
        .join(User, Appointment.provider_id == User.id)
        .filter(Appointment.user_id == current_user.id)
        .all()
    )
    return render_template('user/my_appointments.html', appointments=appointments)

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment and appointment.user_id == current_user.id:
        db.session.delete(appointment)
        db.session.commit()
        flash("Appointment canceled successfully.", "success")
    else:
        flash("Permission denied or invalid appointment.", "danger")
    return redirect(url_for('my_appointments'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash('Access denied. Only users can access this dashboard.', 'danger')
        return redirect(url_for('index'))
        
    appointments = (
        db.session.query(Appointment, User.username.label("provider_name"))
        .filter(Appointment.appointment_status == 'pending')
        .all()
    )

    return render_template('user/user_dashboard.html', user=current_user, appointments=appointments)

#----------------- Provider Usecases -----------------#

@app.route('/provider_dashboard', methods=['GET', 'POST'])
@login_required
def provider_dashboard():
    if current_user.role != 'provider':
        flash('Access denied. Only providers can access this dashboard.', 'danger')
        return redirect(url_for('index'))

    form = UpdateAppointmentStatusForm()
    appointments = (
        db.session.query(Appointment, User.username.label("patient_name"))
        .join(User, Appointment.user_id == User.id)
        .filter(Appointment.provider_id == current_user.id)
        .all()
    )
    
    return render_template('provider/provider_dashboard.html', appointments=appointments, form=form)

@app.route('/update_appointment_status/<int:appointment_id>', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    if current_user.role != 'provider':
        flash('Access denied. Only providers can update appointment status.', 'danger')
        return redirect(url_for('index'))

    form = UpdateAppointmentStatusForm()
    if form.validate_on_submit():
        appointment = Appointment.query.get(appointment_id)
        if appointment and appointment.provider_id == current_user.id:
            appointment.appointment_status = form.status.data
            db.session.commit()
            flash('Appointment status updated successfully!', 'success')
        else:
            flash('Invalid appointment or permission denied.', 'danger')
    return redirect(url_for('provider_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_providers()
    app.run(debug=True)
