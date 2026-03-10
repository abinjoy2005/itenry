import urllib.request
import json

url = 'http://127.0.0.1:5000/api/test-generate'
data = json.dumps({
    "destination": "Munnar",
    "budget": 5000,
    "duration": 2,
    "transport": "car",
    "style": "moderate"
}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers={
    'Content-Type': 'application/json'
})

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.status)
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Failed:")
    print(e.code)
    print(e.read().decode('utf-8'))
