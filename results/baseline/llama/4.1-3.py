import hashlib
import binascii
import os

def generate_password_hash(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def check_password(password, hashed_password):
    stored_salt = hashed_password[:64]
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                stored_salt, 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == hashed_password[64:]

password = "mysecretpassword"
hashed_password = generate_password_hash(password)
print(hashed_password)

is_valid = check_password("mysecretpassword", hashed_password)
print(is_valid)
