from flask import Blueprint, jsonify, request, render_template, current_app
from .storage import load_items, save_items, add_item, update_item, delete_item
from .utils import geocode_location

main = Blueprint('main', __name__)

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
def get_items():
    return jsonify(load_items())

@main.route('/api/items', methods=['POST'])
def post_item():
    data = request.json
    coords = geocode_location(data['location'])
    item = {
        'title': data['title'],
        'description': data['description'],
        'location': data['location'],
        'coords': coords,
        'cost': data['cost'],
        'tags': data['tags'],
        'completed': False,
        'completed_date': None,
        'rating': None,
        'notes': None  # Add notes field with default
    }
    add_item(item)
    return jsonify({'status': 'ok'}), 201

@main.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item_route(item_id):
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415
        
    data = request.json
    
    # For toggle completed requests (with rating/completion date)
    if 'rating' in data or 'completed_date' in data:
        update_item(item_id, data)
    # For simple toggle requests (empty body)
    elif not data:
        update_item(item_id)
    # For edit requests (with other data)
    else:
        update_item(item_id, data)
        
    return jsonify({'status': 'ok'})

@main.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete(item_id):
    delete_item(item_id)
    return jsonify({'status': 'ok'})

