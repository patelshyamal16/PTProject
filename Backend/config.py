import os
from flask_cors import CORS
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

db_path = os.environ.get('DATABASE_PATH', r"C:\Future Horizon\pep-progress-tracker-patelshyamal16\PTProject\Backend\Database\Collection.db")
secret_key = os.environ.get('FLASK_SECRET_KEY', 'Ganesh77')  # Fallback to a default secret key

# Initialize the Flask application
app = Flask(__name__,static_folder= r'C:\Future Horizon\pep-progress-tracker-patelshyamal16\PTProject\Frontend\static', template_folder= r'C:\Future Horizon\pep-progress-tracker-patelshyamal16\PTProject\Frontend\templates')
app.secret_key = secret_key  # Set the secret key for session management
CORS(app)  # Enable CORS for all routes

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize SQLAlchemy
db = SQLAlchemy(app)

def create_user_database(user_id):
    """Creates a user-specific database and sets up the user session."""
    # Define user-specific database path based on user_id
    user_db_path = fr"C:\Future Horizon\pep-progress-tracker-patelshyamal16\PTProject\Backend\Database\UserCollection{user_id}.db"

    # Check that the original database file exists
    if not os.path.exists(db.engine.url.database):
        raise FileNotFoundError("The original Collection.db file does not exist.")
    
    # Ensure the directory for the user-specific database exists
    os.makedirs(os.path.dirname(user_db_path), exist_ok=True)

    # Create a temporary engine for the user-specific database
    user_engine = create_engine(f'sqlite:///{user_db_path}')

    # Reflect tables from the original database (using db.engine)
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    # Create empty tables in the user-specific database, excluding specific tables
    with user_engine.begin() as connection:
        for table_name, table_obj in metadata.tables.items():
            if table_name not in ('user', 'setup_status'):
                table_obj.create(bind=connection)
    
    # Clean up: Dispose user_engine after setup
    user_engine.dispose()

def setup_sessions(user_id):
    """Sets up the user session based on the user ID stored in the session."""
    if user_id:
        # Define the user-specific database path
        user_db_path = fr"C:\Future Horizon\pep-progress-tracker-patelshyamal16\PTProject\Backend\Database\UserCollection{user_id}.db"
        user_engine = create_engine(f'sqlite:///{user_db_path}')
        app.config['SESSION_USER'] = scoped_session(sessionmaker(bind=user_engine))
    else:
        app.config['SESSION_USER'] = None

@app.teardown_appcontext
def remove_sessions(exception=None):
    # Remove the sessions when the app context is torn down
    if 'SESSION_ORIGINAL' in app.config:
        app.config['SESSION_ORIGINAL'].remove()
    if 'SESSION_USER' in app.config and app.config['SESSION_USER'] is not None:
        app.config['SESSION_USER'].remove()

def get_user_session():
    """Helper function to retrieve the user session."""
    return current_app.config.get('SESSION_USER')