# This module defines the Client model structure


class Client:
    def __init__(self, client_id, name, age):
        self.client_id = client_id  # Unique client ID
        self.name = name            # Full name
        self.age = age              # Age
        self.enrolled_programs = []  # List of program names

    def to_dict(self):
        return {
            "id": self.client_id,
            "name": self.name,
            "age": self.age,
            "enrolled_programs": self.enrolled_programs
        }
