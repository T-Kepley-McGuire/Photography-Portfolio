from app import create_app
from flask import render_template

app = create_app()

if __name__ == '__main__':
    # Create the Flask app

    # Run the app
    app.run(debug=True)
