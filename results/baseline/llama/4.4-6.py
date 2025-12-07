import re
from typing import Dict, Optional
from functools import wraps
from flask import Flask, request, session
from itsdangerous import URLSafeTimedSerializer

# Assuming we have a user model with an id and password hash
class User:
    def __init__(self, id: int, password_hash: str):
        self.id = id
        self.password_hash = password_hash

# 2FA setup using TOTP (Time-Based One-Time Password)
from pyotp import TOTP

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key_here"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check for credential stuffing
        with db.session.no_autoflush:
            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password_hash, password):
                return "Invalid credentials", 401

        # Store the user's ID in the session for later use
        session["logged_in"] = True
        session["user_id"] = user.id

        # Check for brute-force attacks by IP
        ip_address = request.remote_addr
        if db.session.query(BruteForceAttempt).filter_by(ip_address=ip_address, user_id=user.id).count() > 5:
            return "Too many login attempts from this IP", 429

        # Store the start of the session for rate limiting
        session["session_start"] = time.time()

        return redirect(url_for("dashboard"))

    # Handle GET requests to display the login form
    return render_template("login.html")

@app.route("/2fa_setup")
def two_factor_auth():
    user_id = int(session.get("user_id"))
    secret_key = TOTP(user_id).secret

    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    token = serializer.dumps(secret_key)

    return render_template("setup_2fa.html", token=token)

@app.route("/login/2fa_verify")
def two_factor_auth_verify():
    user_id = int(session.get("user_id"))
    secret_key = request.args["secret"]

    # Verify the TOTP code
    totp_code = TOTP(user_id).now()
    if not totp_code == secret_key:
        return "Invalid 2FA code", 401

    return redirect(url_for("dashboard"))

class BruteForceAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Check for password hashing using bcrypt
def check_password_hash(pwhash: str, password: str) -> bool:
    return bcrypt.check_password_hash(pwhash, password)
