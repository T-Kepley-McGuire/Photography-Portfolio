from flask import Flask
from app.config import Config
from app.routes import main  # Import the blueprint
from app.models import db  # Import db here
from app import create_app



if __name__ == '__main__':
    # Create the Flask app
    app = create_app()

    # Run the app
    app.run(debug=True)
