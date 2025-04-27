# crypto_helper.py
from cryptography.fernet import Fernet

# Generate key ONCE and save it securely
# KEY = b'YOUR_GENERATED_KEY_HERE'
key = Fernet.generate_key()

# cipher = Fernet(KEY)

print(key.decode()) 


# def encrypt_data(data):
#     return cipher.encrypt(data.encode()).decode()

# def decrypt_data(data):
#     return cipher.decrypt(data.encode()).decode()
