from flask import Flask, request, jsonify
from models import Client
from storage import clients, health_programs
from utils import search_clients

app = Flask(__name__)

# Create a health program
@app.route('/programs', methods=['POST'])
def create_program():
    program = request.json.get('name')
    if not program:
        return jsonify({"error": "Program name is required."}), 400
    if program in health_programs:
        return jsonify({"error": "Program already exists."}), 400

    health_programs.append(program)
    return jsonify({"message": f"Program '{program}' created successfully."}), 201

# Register a new client
@app.route('/clients', methods=['POST'])
def register_client():
    data = request.json
    if 'name' not in data or 'age' not in data:
        return jsonify({"error": "Name and age are required."}), 400

    client_id = str(len(clients) + 1)
    new_client = Client(client_id, data['name'], data['age'])
    clients[client_id] = new_client
    return jsonify({"message": "Client registered successfully.", "client_id": client_id}), 201

# Enroll a client in health programs
@app.route('/clients/<client_id>/enroll', methods=['POST'])
def enroll_client(client_id):
    if client_id not in clients:
        return jsonify({"error": "Client not found."}), 404

    programs = request.json.get('programs', [])
    client = clients[client_id]

    for program in programs:
        if program in health_programs and program not in client.enrolled_programs:
            client.enrolled_programs.append(program)

    return jsonify({"message": "Enrollment successful.", "enrolled_programs": client.enrolled_programs})

# Search for a client by name
@app.route('/clients/search', methods=['GET'])
def search_client():
    query = request.args.get('name', '')
    results = search_clients(query)
    return jsonify([c.to_dict() for c in results])

# View a client's profile
@app.route('/clients/<client_id>', methods=['GET'])
def view_client(client_id):
    client = clients.get(client_id)
    if not client:
        return jsonify({"error": "Client not found."}), 404
    return jsonify(client.to_dict())

@app.route('/')
def home():
    return "🩺 Health Information System is running!"


if __name__ == '__main__':
    print("✅ Flask app is starting...")
    app.run(debug=True)
