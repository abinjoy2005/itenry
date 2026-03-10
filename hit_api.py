import requests
import json

url = 'http://127.0.0.1:5000/api/generate-itinerary'
headers = {'Content-Type': 'application/json'}
payload = {
    "origin": "Kochi",
    "destination": "Munnar",
    "budget": 1000,
    "duration": 1,
    "style": "moderate",
    "transport": "car",
    "age": 30,
    "interests": [],
    "cuisine_preferences": [],
    "children": False
}

# we need a token to hit this endpoint! 
# Let me bypass it by creating a test token or just looking at the return of mcts manually with the EXACT same things.
