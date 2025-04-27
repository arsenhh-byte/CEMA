from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
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

        flash('Signup successful. Please log in.', 'success')
        return redirect(url_for('login'))
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


@app.route('/register-client', methods=['GET', 'POST'])
def register_client():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = f"{request.form['first_name']} {request.form['last_name']}"
        new_client = Client(
            name=name,
            dob=request.form['dob'],
            gender=request.form['gender'],
            contact=request.form['contact'],
            address=request.form['address']
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Client registered successfully.', 'success')
        return redirect(url_for('clients_page'))
    
    return render_template('register_client.html')


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

# --- PROGRAM ROUTES ---

@app.route('/programs')
def programs_page():
    programs = ProgramModel.query.all()
    return render_template('programs_page.html', programs=programs)

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
            query = query.filter(Client.dob >= after_date)
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

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
