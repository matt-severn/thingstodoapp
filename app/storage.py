import json
import datetime
from pathlib import Path

DATA_PATH = Path(__file__).parent / 'data.json'

def load_items():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def save_items(items):
    with open(DATA_PATH, 'w') as f:
        json.dump(items, f, indent=2)

def add_item(item):
    items = load_items()
    items.append(item)
    save_items(items)

def update_item(item_id, data=None):
    items = load_items()
    if 0 <= item_id < len(items):
        if data is None:
            # Simple toggle
            items[item_id]['completed'] = not items[item_id].get('completed', False)
        else:
            # Update with provided data
            if 'completed' in data:
                items[item_id]['completed'] = data['completed']
            if 'rating' in data:
                items[item_id]['rating'] = data['rating']
            if 'completed_date' in data:
                items[item_id]['completed_date'] = data['completed_date']
            if 'notes' in data:  # Add notes handling
                items[item_id]['notes'] = data['notes']
            # Update other fields if present
            items[item_id].update({k: v for k, v in data.items() 
                                 if k not in ['rating', 'completed_date', 'completed', 'notes']})
    save_items(items)

def delete_item(item_id):
    items = load_items()
    if 0 <= item_id < len(items):
        items.pop(item_id)
    save_items(items)
