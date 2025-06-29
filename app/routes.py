from flask import Blueprint, jsonify, request, render_template, current_app, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Item
from .storage import load_items, save_items, add_item, update_item, delete_item
from .utils import geocode_location
import json
from pathlib import Path

main = Blueprint('main', __name__)
DATA_PATH = Path(__file__).parent / 'data.json'

@main.route('/')
def index():
    return render_template('index.html', google_api_key=current_app.config['GOOGLE_API_KEY'])

@main.route('/test-key')
def test_key():
    # This shows how the key is available server-side but not exposed
    return f"""
    <h1>Key Test</h1>
    <p>Key exists: {'yes' if current_app.config['GOOGLE_API_KEY'] else 'no'}</p>
    <p>Key value: {'*****' if current_app.config['GOOGLE_API_KEY'] else 'not set'}</p>
    """

@main.route('/api/items', methods=['GET'])
@login_required
def get_items():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'location': item.location,
        'coords': {'lat': item.lat, 'lng': item.lng},
        'cost': item.cost,
        'tags': item.tags.split(',') if item.tags else [],
        'completed': item.completed,
        'rating': item.rating,
        'completed_date': item.completed_date,
        'notes': item.notes
    } for item in items])

@main.route('/api/items', methods=['POST'])
@login_required
def post_item():
    data = request.json
    coords = geocode_location(data['location'])
    
    item = Item(
        user_id=current_user.id,
        title=data['title'],
        description=data.get('description', ''),
        location=data['location'],
        lat=coords['lat'],
        lng=coords['lng'],
        cost=float(data.get('cost', 0)),
        tags=','.join(data.get('tags', [])),
        completed=False
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'status': 'ok'}), 201

@main.route('/api/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item_route(item_id):
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415
        
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
        
    data = request.json
    
    # Update fields if provided
    if 'title' in data:
        item.title = data['title']
    if 'description' in data:
        item.description = data['description']
    if 'location' in data:
        coords = geocode_location(data['location'])
        item.location = data['location']
        item.lat = coords['lat']
        item.lng = coords['lng']
    if 'cost' in data:
        item.cost = float(data['cost'])
    if 'tags' in data:
        item.tags = ','.join(data['tags'])
    
    # For completion status with rating/date
    if 'rating' in data or 'completed_date' in data:
        item.completed = data.get('completed', True)
        item.rating = data.get('rating')
        item.completed_date = data.get('completed_date')
        item.notes = data.get('notes', '')
    
    # For simple toggle
    elif 'completed' in data:
        item.completed = data['completed']
        if not data['completed']:
            item.rating = None
            item.completed_date = None
            item.notes = None
    
    db.session.commit()
    return jsonify({'status': 'ok'})

@main.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete(item_id):
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
        
    db.session.delete(item)
    db.session.commit()
    return jsonify({'status': 'ok'})

@main.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    # Migrate existing data for admin
    if user.email == "admin@example.com" and DATA_PATH.exists():
        # Check if admin already has items
        if Item.query.filter_by(user_id=user.id).count() == 0:
            with open(DATA_PATH, 'r') as f:
                items = json.load(f)
                for item_data in items:
                    coords = geocode_location(item_data['location'])
                    item = Item(
                        user_id=user.id,
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
    
    login_user(user)
    return jsonify({'status': 'success'})