from flask import Flask
from flask_login import LoginManager
from .models import db, User, Item
from .routes import main
import os
import json
from pathlib import Path
from .utils import geocode_location

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "default-secret-key")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    DATA_PATH = Path(__file__).parent / 'data.json'  # Define DATA_PATH
    
    with app.app_context():
        db.create_all()
        admin_email = "admin@example.com"
        admin = User.query.filter_by(email=admin_email).first()
        
        if not admin:
            admin = User(email=admin_email, is_admin=True)
            admin.set_password("admin_password")
            db.session.add(admin)
            db.session.commit()
        
        # Migrate data if admin exists and has no items
        if admin and Item.query.filter_by(user_id=admin.id).count() == 0 and DATA_PATH.exists():
            with open(DATA_PATH, 'r') as f:
                items = json.load(f)
                for item_data in items:
                    coords = geocode_location(item_data['location'])
                    item = Item(
                        user_id=admin.id,
                        title=item_data['title'],
                        description=item_data.get('description', ''),
                        location=item_data['location'],
                        lat=coords['lat'],
                        lng=coords['lng'],
                        cost=float(item_data.get('cost', 0)),
                        tags=','.join(item_data.get('tags', [])),
                        completed=item_data.get('completed', False),
                        rating=item_data.get('rating'),
                        completed_date=item_data.get('completed_date'),
                        notes=item_data.get('notes')
                    )
                    db.session.add(item)
                db.session.commit()
    
    app.register_blueprint(main)

    # Validate that API key exists
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("No GOOGLE_API_KEY set in environment variables")
    
    app.config['GOOGLE_API_KEY'] = google_api_key
    return app