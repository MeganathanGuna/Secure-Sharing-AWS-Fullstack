from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(input_file, output_file, key):
    fernet = Fernet(key)

    with open(input_file, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)

    with open(output_file, "wb") as f:
        f.write(encrypted_data)

def decrypt_file(input_file, output_file, key):
    fernet = Fernet(key)

    with open(input_file, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)
