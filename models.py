from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Many-to-many relationship between clients and programs
enrollments = db.Table('enrollments',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id')),
    db.Column('program_id', db.Integer, db.ForeignKey('program_model.id'))
)

# Doctor Model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # A doctor can create many programs
    programs = db.relationship('ProgramModel', backref='creator', lazy=True)

# Client Model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    # A client can enroll into multiple programs
    programs = db.relationship('ProgramModel', secondary=enrollments, back_populates='clients')

# Program Model
class ProgramModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    # A program can have multiple enrolled clients
    clients = db.relationship('Client', secondary=enrollments, back_populates='programs')
