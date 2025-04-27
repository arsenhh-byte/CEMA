from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from models import db, Client, ProgramModel, Doctor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import io

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthsystem.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'   # Or your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'your_email_password'   # Your app-specific password (don't use real password)

mail = Mail(app)
# Initialize database and Bcrypt
db.init_app(app)
bcrypt = Bcrypt(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# --- AUTH ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']

        existing_doctor = Doctor.query.filter_by(username=username).first()
        if existing_doctor:
            flash('Username already exists.', 'danger')
            return redirect(url_for('signup'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_doctor = Doctor(username=username, name=name, password=hashed_pw)
        db.session.add(new_doctor)
        db.session.commit()

        # Auto-login and redirect to dashboard
        session['logged_in'] = True
        session['doctor'] = new_doctor.name
        session['doctor_id'] = new_doctor.id
        flash(f"Welcome {new_doctor.name}!", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and bcrypt.check_password_hash(doctor.password, password):
            session['logged_in'] = True
            session['doctor'] = doctor.name
            session['doctor_id'] = doctor.id
            flash(f"Welcome {doctor.name}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# --- MAIN DASHBOARD ---

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    programs = ProgramModel.query.filter_by(created_by=session['doctor_id']).all()
    clients = Client.query.all()
    return render_template('dashboard.html', programs=programs, clients=clients)

# Dasboard route for auto refresh
@app.route('/api/dashboard-data')
def api_dashboard_data():
    programs = ProgramModel.query.all()
    clients = Client.query.all()
    return jsonify({
        "programs": [
            {"name": p.name, "clients": [{"name": c.name} for c in p.clients]} for p in programs
        ],
        "clients": [{"name": c.name} for c in clients]
    })


# --- CLIENT ROUTES ---

@app.route('/clients')
def clients_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    query = request.args.get('search', '')
    if query:
        clients = Client.query.filter(Client.name.ilike(f"%{query}%")).all()
    else:
        clients = Client.query.all()

    # If it's an AJAX (fetch) request, only return the HTML for the clients list
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/client_list.html', clients=clients)
    
    return render_template('clients_page.html', clients=clients, query=query)

#email client route
@app.route('/email-clients-pdf', methods=['POST'])
def email_clients_pdf():
    if not session.get('logged_in'):
        return jsonify({"success": False}), 401

    try:
        raw_emails = request.form['emails']
        recipient_list = [email.strip() for email in raw_emails.split(',') if email.strip()]

        if not recipient_list:
            return jsonify({"success": False}), 400

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, "This is the client registry!")
        pdf.save()
        buffer.seek(0)

        msg = Message('Client Registry Report', sender=app.config['MAIL_USERNAME'], recipients=recipient_list)
        msg.body = 'Attached is the latest client registry report.'
        msg.attach('client_registry.pdf', 'application/pdf', buffer.read())

        mail.send(msg)

        return jsonify({"success": True})
    except Exception as e:
        print('Email error:', e)
        return jsonify({"success": False}), 500

#create client route
@app.route('/api/create-client', methods=['POST'])
def api_create_client():
    data = request.json
    new_client = Client(
        name=f"{data['first_name']} {data['last_name']}",
        dob=data['dob'],
        gender=data['gender'],
        contact=data['contact'],
        address=data['address']
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"message": "Client created successfully."}), 201

#Register client route
@app.route('/register-client', methods=['GET', 'POST'])
def register_client():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        full_name = f"{first_name} {last_name}"
        dob = request.form['dob']
        gender = request.form['gender']
        country_code = request.form['country_code']
        phone = request.form['contact']
        full_contact = f"{country_code}{phone}"
        email = request.form['email']  

        new_client = Client(
            name=full_name,
            dob=dob,
            gender=gender,
            contact=full_contact,
            address=email 
        )

        db.session.add(new_client)
        db.session.commit()

        flash('Client registered successfully.', 'success')
        return redirect(url_for('clients_page'))
    
    return render_template('register_client.html')



# Client Profile Route
@app.route('/client/<int:client_id>')
def view_client(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template('view_client.html', client=client)

@app.route('/edit-client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        client.name = f"{request.form['first_name']} {request.form['last_name']}"
        client.dob = request.form['dob']
        client.gender = request.form['gender']
        client.contact = request.form['contact']
        client.address = request.form['address']
        db.session.commit()
        flash('Client updated.', 'success')
        return redirect(url_for('view_client', client_id=client_id))
    first, *last = client.name.split()
    return render_template('edit_client.html', client=client, first_name=first, last_name=" ".join(last))

# API route for single client profile
@app.route('/api/clients/<int:client_id>', methods=['GET'])
def api_client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify({
        "id": client.id,
        "name": client.name,
        "dob": client.dob,
        "gender": client.gender,
        "contact": client.contact,
        "address": client.address,
        "programs": [program.name for program in client.programs]
    })

@app.route('/delete-client/<int:client_id>')
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted.', 'success')
    return redirect(url_for('clients_page'))

@app.route('/enroll-client/<int:client_id>', methods=['GET', 'POST'])
def enroll_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        selected_programs = request.form.getlist('programs')
        programs = ProgramModel.query.filter(ProgramModel.id.in_(selected_programs)).all()
        client.programs = programs
        db.session.commit()
        flash('Client enrollment updated.', 'success')
        return redirect(url_for('view_client', client_id=client_id))
    programs = ProgramModel.query.all()
    return render_template('enroll_client.html', client=client, programs=programs)

@app.route('/api/enroll-client', methods=['POST'])
def api_enroll_client():
    data = request.json
    client = Client.query.get_or_404(data['client_id'])
    programs = ProgramModel.query.filter(ProgramModel.id.in_(data['program_ids'])).all()
    client.programs = programs
    db.session.commit()
    return jsonify({"message": "Client enrolled successfully."}), 200

@app.route('/api/delete-client/<int:id>', methods=['DELETE'])
def api_delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted successfully."}), 200
# --- PROGRAM ROUTES ---

@app.route('/programs')
def programs_page():
    programs = ProgramModel.query.all()
    doctors = Doctor.query.all()
    return render_template('programs_page.html', programs=programs, doctors=doctors)

#create program route
@app.route('/api/create-program', methods=['POST'])
def api_create_program():
    data = request.json
    new_program = ProgramModel(
        name=data['name'],
        created_by=session['doctor_id']
    )
    db.session.add(new_program)
    db.session.commit()
    return jsonify({"message": "Program created successfully."}), 201

@app.route('/programs/new', methods=['GET', 'POST'])
def create_program():
    if request.method == 'POST':
        name = request.form['name']
        doctor_id = session['doctor_id']
        new_program = ProgramModel(name=name, created_by=doctor_id)
        db.session.add(new_program)
        db.session.commit()
        flash('Program created successfully.', 'success')
        return redirect(url_for('programs_page'))
    return render_template('create_program.html')

@app.route('/programs/edit/<int:program_id>', methods=['GET', 'POST'])
def edit_program(program_id):
    program = ProgramModel.query.get_or_404(program_id)
    if request.method == 'POST':
        program.name = request.form['name']
        db.session.commit()
        flash('Program updated.', 'success')
        return redirect(url_for('programs_page'))
    return render_template('edit_program.html', program=program)

@app.route('/programs/delete/<int:program_id>')
def delete_program(program_id):
    program = ProgramModel.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    flash('Program deleted successfully.', 'info')
    return redirect(url_for('programs_page'))

# --- SUMMARY ROUTE ---

@app.route('/summary')
def summary_page():
    doctor_id = session.get('doctor_id')
    programs = ProgramModel.query.filter_by(created_by=doctor_id).all()
    total_programs = len(programs)
    total_clients = len(Client.query.all())
    return render_template('summary_page.html', total_programs=total_programs, total_clients=total_clients)

# --- API ROUTES ---

@app.route('/api/clients')
def api_clients():
    clients = Client.query.all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "dob": c.dob,
            "gender": c.gender,
            "contact": c.contact,
            "address": c.address,
            "programs": [p.name for p in c.programs]
        } for c in clients
    ])

@app.route('/api/programs')
def api_programs():
    programs = ProgramModel.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "created_by": p.creator.name if p.creator else None,
            "enrolled_clients": [c.name for c in p.clients]
        } for p in programs
    ])

# --- PDF DOWNLOAD (Advanced Feature) ---

@app.route('/download-clients-pdf')
def download_clients_pdf():
    program_filter = request.args.get('program')
    after_date = request.args.get('after')

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Filtered Client Registry Report")
    y -= 30
    pdf.setFont("Helvetica", 10)

    query = Client.query
    if program_filter:
        program = ProgramModel.query.filter_by(name=program_filter).first()
        if program:
            query = query.filter(Client.programs.contains(program))

    if after_date:
        try:
            after_date_obj = datetime.strptime(after_date, "%Y-%m-%d")
            query = query.filter(Client.dob >= after_date_obj)
        except:
            pass

    clients = query.all()
    for c in clients:
        pdf.drawString(40, y, f"{c.name} | DOB: {c.dob} | Contact: {c.contact} | Programs: {', '.join([p.name for p in c.programs])}")
        y -= 15
        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="client_registry_filtered.pdf", mimetype='application/pdf')

#Export to CSV (Advanced Feature)
import csv
@app.route('/download-clients-csv')
def download_clients_csv():
    # Optional query parameters
    program_filter = request.args.get('program')
    after_date = request.args.get('after')

    query = Client.query

    # Apply filters
    if program_filter:
        program = ProgramModel.query.filter_by(name=program_filter).first()
        if program:
            query = query.filter(Client.programs.contains(program))

    if after_date:
        try:
            after_date_obj = datetime.strptime(after_date, "%Y-%m-%d")
            query = query.filter(Client.dob >= after_date_obj)
        except ValueError:
            pass  # Ignore bad dates

    clients = query.all()

    # Create in-memory CSV
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Header
    writer.writerow(["Name", "DOB", "Gender", "Contact", "Address", "Programs"])

    # Write client rows
    for client in clients:
        programs = ", ".join([p.name for p in client.programs])
        writer.writerow([client.name, client.dob, client.gender, client.contact, client.address, programs])

    buffer.seek(0)

    # Return as downloadable file
    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name="filtered_clients.csv"
    )

# Export programs to CSV
@app.route('/export-programs-csv')
def export_programs_csv():
    programs = ProgramModel.query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow(['Program Name', 'Created By', 'Number of Clients'])

    for program in programs:
        writer.writerow([
            program.name,
            program.creator.name if program.creator else 'Unknown',
            len(program.clients)
        ])

    output.seek(0)

    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=programs_list.csv"}
    )


# Export programs to PDF
@app.route('/export-programs-pdf')
def export_programs_pdf():
    programs = ProgramModel.query.all()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Programs Report")
    y -= 30
    pdf.setFont("Helvetica", 11)

    for program in programs:
        created_by = program.creator.name if program.creator else 'Unknown'
        enrolled_clients = len(program.clients)
        pdf.drawString(40, y, f"{program.name} | Created by: {created_by} | {enrolled_clients} Clients")
        y -= 20
        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="programs_report.pdf", mimetype='application/pdf')

# --- Security Configurations ---
app.config['SESSION_COOKIE_SECURE'] = True      # Cookie sent only via HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True    # Cookie can't be accessed via JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # Protect against CSRF
app.config['REMEMBER_COOKIE_SECURE'] = True     # If using 'Remember Me' login (future-proof)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 # Sessions expire after 1 hour (in seconds)


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
