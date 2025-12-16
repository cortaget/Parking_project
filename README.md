🅿️ Parking Route API

    Find the nearest parking spot and build a route from the user's current location in Prague.

![Python](https://img.shields.io/badge/python-3.8+-reenrange of Contents

    Features

    Installation

    API Documentation

    Usage Examples

    Error Handling

✨ Features

    🎯 Finds nearest available parking spot in specified radius

    🗺️ Builds real route along actual roads using OpenStreetMap

    📍 Returns GPS coordinates for map visualization

    ⚡ Fast response with efficient pathfinding algorithms

    🔄 Mock API included for testing

🚀 Installation

bash
# Clone the repository
git clone https://github.com/yourusername/parking-route-api.git
cd parking-route-api

# Install dependencies
pip install flask osmnx networkx requests

# Run the server
python app.py

Server will start at http://localhost:5000
📖 API Documentation
Endpoint

text
POST /find-parking-route

Request Parameters
Parameter	Type	Required	Description
user_lat	float	✅ Yes	User's current latitude (-90 to 90)
user_lon	float	✅ Yes	User's current longitude (-180 to 180)
search_radius	integer	❌ No	Search radius in meters (default: 1000)
Request Example

json
{
    "user_lat": 50.0755,
    "user_lon": 14.4378,
    "search_radius": 1000
}

Success Response

Code: 200 OK

json
{
    "status": "success",
    "user_location": {
        "lat": 50.0755,
        "lon": 14.4378
    },
    "parking": {
        "position": {
            "lat": 50.0785,
            "lon": 14.4328
        },
        "address": {
            "postal_code": "11000",
            "street": "Národní třída",
            "house_number": "40"
        },
        "capacity": 5,
        "date": "2025-12-16T22:00:00",
        "distance_meters": 488.45
    },
    "route_length_meters": 625.12,
    "path": [
        [50.0758506, 14.4375158],
        [50.0758701, 14.4374152],
        ...
    ]
}

Error Response

Code: 400 BAD REQUEST

json
{
    "status": "error",
    "message": "Missing coordinates or invalid format"
}

Code: 404 NOT FOUND

json
{
    "status": "error",
    "message": "No parking spots found within the specified radius"
}

Code: 500 INTERNAL SERVER ERROR

json
{
    "status": "error",
    "message": "Route building error: [details]"
}

💡 Usage Examples
cURL

bash
curl -X POST http://localhost:5000/find-parking-route \
  -H "Content-Type: application/json" \
  -d '{"user_lat": 50.0755, "user_lon": 14.4378}'

Python

python
import requests

response = requests.post(
    "http://localhost:5000/find-parking-route",
    json={
        "user_lat": 50.0755,
        "user_lon": 14.4378,
        "search_radius": 1500
    }
)

data = response.json()
print(f"Route length: {data['route_length_meters']} meters")
print(f"Parking: {data['parking']['address']['street']}")

JavaScript (Fetch API)

javascript
fetch('http://localhost:5000/find-parking-route', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_lat: 50.0755,
        user_lon: 14.4378
    })
})
.then(response => response.json())
.then(data => {
    console.log('Nearest parking:', data.parking.address.street);
    console.log('Route coordinates:', data.path);
});

PowerShell (Windows)

powershell
Invoke-WebRequest -Uri http://localhost:5000/find-parking-route `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_lat": 50.0755, "user_lon": 14.4378}'

🛠️ Error Handling
Status Code	Description
200	✅ Success - Route found
400	❌ Bad Request - Invalid or missing parameters
404	❌ Not Found - No parking spots in radius
500	❌ Server Error - Route calculation failed
🔧 Configuration

To use real Parking API instead of mock, update in app.py:

python
PARKING_API_URL = "https://your-real-api.com/parking"

📝 License

MIT License - feel free to use this project for your needs.
🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

Made with ❤️ for Prague parking navigation
