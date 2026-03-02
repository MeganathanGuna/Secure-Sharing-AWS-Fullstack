# key_manager.py
from cryptography.fernet import Fernet

def generate_master_key():
    return Fernet.generate_key()

def encrypt_data_key(data_key, master_key):
    f = Fernet(master_key)
    return f.encrypt(data_key)

def decrypt_data_key(encrypted_key, master_key):
    f = Fernet(master_key)
    return f.decrypt(encrypted_key)