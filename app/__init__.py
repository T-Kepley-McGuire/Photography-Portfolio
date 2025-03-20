# app/__init__.py

from flask import Flask, render_template
from app.config import Config
from app.models import db
from app.routes import main

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    
    db.init_app(app)
    app.register_blueprint(main)
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html'), 404
    
    return app
