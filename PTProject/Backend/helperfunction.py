from config import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

def is_valid_name(name):
    return name.isalpha()

def is_valid_email(email):
    return "@" in email and email.endswith(".com")

def is_valid_password(password):
    return len(password) >= 16

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def user_exists(email, password):
    # Check if the user exists and verify the password
    user = User.query.filter_by(email=email).first()
    return user is not None and check_password_hash(user.password, password)

def add_user_to_database(first_name, last_name, email, password):
    # Create a new user instance
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Hash the password
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
    
    # Add the user to the session and commit
    db.session.add(new_user)
    db.session.commit()
    return new_user