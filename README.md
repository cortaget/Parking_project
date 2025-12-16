PARKING ROUTE API

Find the nearest parking spot and build a route from the user's current location.
HOW TO USE
ENDPOINT

/find-parking-route

Method: POST

Input type: JSON

Input: user_lat, user_lon, search_radius (optional)

    user_lat - latitude of user's current location

    user_lon - longitude of user's current location

    search_radius - parking search radius in meters (default 1000)

Returns:

    User and nearest parking information

    Route length in meters

    List of GPS coordinates for map display

Request:

address: http://localhost:5000/find-parking-route

json
# header
Content-Type: application/json

# body
{
    "user_lat": 50.0755,
    "user_lon": 14.4378,
    "search_radius": 1000  // optional
}

Response:

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

Error Response:

json
{
    "status": "error",
    "message": "Error description"
}

USAGE EXAMPLES

cURL (Linux/Mac):

bash
curl -X POST http://localhost:5000/find-parking-route \
  -H "Content-Type: application/json" \
  -d '{"user_lat": 50.0755, "user_lon": 14.4378}'

PowerShell (Windows):

powershell
Invoke-WebRequest -Uri http://localhost:5000/find-parking-route `
  -Method POST -ContentType "application/json" `
  -Body '{"user_lat": 50.0755, "user_lon": 14.4378}'

Python:

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

JavaScript (fetch):

javascript
fetch('http://localhost:5000/find-parking-route', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        user_lat: 50.0755,
        user_lon: 14.4378
    })
})
.then(response => response.json())
.then(data => console.log(data.path));

ERROR CODES

    400 - Bad request (missing coordinates or invalid format)

    404 - No parking spots found within the specified radius

    500 - Internal server error (route building error)
