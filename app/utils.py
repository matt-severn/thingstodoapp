import requests
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def geocode_location(address):
    if not GOOGLE_API_KEY:
        return {'lat': 0, 'lng': 0}
    url = f'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': GOOGLE_API_KEY}
    res = requests.get(url, params=params).json()
    if res['results']:
        location = res['results'][0]['geometry']['location']
        return {'lat': location['lat'], 'lng': location['lng']}
    return {'lat': 0, 'lng': 0}
