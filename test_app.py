import pytest
from app import app, db
from models import Doctor

@pytest.fixture
def client():
    # Setup: configure app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for testing
    app.config['WTF_CSRF_ENABLED'] = False

    # Create test client
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client  # provide client to tests

    # Teardown: clean up
    with app.app_context():
        db.drop_all()

def test_home_redirect(client):
    """Test if '/' redirects to login page."""
    response = client.get('/')
    assert response.status_code == 302  # Redirect
    assert '/login' in response.location

def test_doctor_signup_and_login(client):
    """Test doctor signup and login flow."""
    # Signup
    response = client.post('/signup', data={
        'username': 'testdoc',
        'name': 'Test Doctor',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Signup successful' in response.data

    # Login
    response = client.post('/login', data={
        'username': 'testdoc',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Welcome Test Doctor' in response.data

def test_register_client(client):
    """Test registering a new client."""
    # First, create a doctor and log in
    client.post('/signup', data={
        'username': 'testdoc2',
        'name': 'Test Doctor2',
        'password': 'password123'
    }, follow_redirects=True)
    client.post('/login', data={
        'username': 'testdoc2',
        'password': 'password123'
    }, follow_redirects=True)

    # Register client
    response = client.post('/register-client', data={
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '1990-01-01',
        'gender': 'Male',
        'contact': '712345678',
        'address': '123 Street',
        'country_code': '+254',
        'email': 'john.doe@example.com'
    }, follow_redirects=True)

    assert b'Client registered successfully' in response.data

def test_api_clients(client):
    """Test API fetching clients."""
    # Should return empty list initially
    response = client.get('/api/clients')
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert isinstance(data, list)

def test_api_programs(client):
    """Test API fetching programs."""
    # Should return empty list initially
    response = client.get('/api/programs')
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert isinstance(data, list)

#download pdf 
def test_generate_pdf(client):
    response = client.get('/download-clients-pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
