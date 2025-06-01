from flask import Flask
from .routes import main
import os

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    
    # Validate that API key exists
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("No GOOGLE_API_KEY set in environment variables")
    
    app.config['GOOGLE_API_KEY'] = google_api_key
    return app