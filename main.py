from flask import Flask, request, jsonify
import math
import osmnx as ox
import networkx as nx
import requests

app = Flask(__name__)

# ИЗМЕНЕНО: URL Prague Parking API
PARKING_API_URL =  "http://localhost:5000/mock-parking-api"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ИЗМЕНЕНО: Адаптировано под новый формат parking API
def find_closest_street(my_lat, my_lon, streets):
    """
    streets — список объектов вида:
    {
        "position": {"lat": ..., "lon": ...},
        "address": {"street": "...", "number": ...}
    }
    """
    closest = None
    min_distance = float("inf")

    for s in streets:
        lat = s["position"]["lat"]
        lon = s["position"]["lon"]

        dist = haversine(my_lat, my_lon, lat, lon)

        if dist < min_distance:
            min_distance = dist
            closest = s

    return closest, min_distance


def build_route(origin_lat, origin_lon, dest_lat, dest_lon, radius=2000):
    """
    Строит маршрут от origin до destination используя OSMnx

    Args:
        origin_lat: широта начальной точки
        origin_lon: долгота начальной точки
        dest_lat: широта конечной точки
        dest_lon: долгота конечной точки
        radius: радиус загрузки графа дорог в метрах

    Returns:
        dict: {
            "route_length": длина маршрута в метрах,
            "path_coordinates": список координат [(lat, lon), ...]
        }
    """
    try:
        # Загружаем граф дорог вокруг начальной точки
        G = ox.graph_from_point((origin_lat, origin_lon), dist=radius, network_type='drive')

        # Находим ближайшие узлы графа к начальной и конечной точкам
        origin_node = ox.distance.nearest_nodes(G, origin_lon, origin_lat)
        dest_node = ox.distance.nearest_nodes(G, dest_lon, dest_lat)

        # Находим кратчайший путь
        route = nx.shortest_path(G, origin_node, dest_node, weight='length')
        route_length = nx.shortest_path_length(G, origin_node, dest_node, weight='length')

        # Преобразуем маршрут в координаты
        path_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

        return {
            "route_length": round(route_length, 2),
            "path_coordinates": path_coords
        }
    except Exception as e:
        raise Exception(f"Ошибка построения маршрута: {str(e)}")


# НОВАЯ ФУНКЦИЯ: Получение списка парковок от Prague Parking API
def get_parking_spots(user_lat, user_lon, radius=1000):
    """
    Отправляет запрос к Prague Parking API и получает список парковок

    Args:
        user_lat: широта пользователя
        user_lon: долгота пользователя
        radius: радиус поиска в метрах (по умолчанию 1000м = 1км)

    Returns:
        list: список парковок или None при ошибке
    """
    try:
        # Формируем данные согласно документации API
        payload = {
            "position": {
                "lat": user_lat,
                "lon": user_lon
            },
            "radius": radius
        }

        headers = {
            "Content-Type": "application/json"
        }

        # ВАЖНО: Документация говорит GET, но с JSON body
        # Это нестандартно, но делаем как в документации
        response = requests.get(
            PARKING_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            parking_spots = response.json()

            # Проверяем что получили список
            if isinstance(parking_spots, list) and len(parking_spots) > 0:
                return parking_spots
            else:
                print("API вернул пустой список парковок")
                return None
        else:
            print(f"Ошибка от Parking API: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("Таймаут при запросе к Parking API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к Parking API: {str(e)}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        return None


# НОВАЯ ФУНКЦИЯ: Находит ближайшую парковку из списка
def find_closest_parking(user_lat, user_lon, parking_spots):
    """
    Находит ближайшую парковку к пользователю из списка

    Args:
        user_lat: широта пользователя
        user_lon: долгота пользователя
        parking_spots: список парковок от API

    Returns:
        tuple: (ближайшая_парковка, расстояние_в_метрах)
    """
    closest_parking = None
    min_distance = float("inf")

    for parking in parking_spots:
        parking_lat = parking["position"]["lat"]
        parking_lon = parking["position"]["lon"]

        # Используем твою функцию haversine
        distance = haversine(user_lat, user_lon, parking_lat, parking_lon)

        if distance < min_distance:
            min_distance = distance
            closest_parking = parking

    return closest_parking, min_distance


# ГЛАВНЫЙ ENDPOINT: Получает местоположение пользователя, находит парковку, строит маршрут
@app.route('/find-parking-route', methods=['POST'])
def find_parking_route():
    """
    POST /find-parking-route

    Принимает от фронтенда: {
        "user_lat": 50.0755,
        "user_lon": 14.4378,
        "search_radius": 1000  // опционально, по умолчанию 1000м
    }

    Процесс:
    1. Получает координаты пользователя от фронтенда
    2. Запрашивает список парковок у Prague Parking API
    3. Находит ближайшую парковку
    4. Строит маршрут от пользователя до парковки
    5. Возвращает маршрут на фронтенд

    Возвращает: {
        "status": "success",
        "user_location": {"lat": ..., "lon": ...},
        "parking": {
            "position": {"lat": ..., "lon": ...},
            "address": {...},
            "capacity": ...,
            "distance_meters": ...
        },
        "route_length_meters": ...,
        "path": [[lat, lon], [lat, lon], ...]
    }
    """
    data = request.get_json(silent=True)

    # Валидация входных данных
    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON данные не предоставлены"
        }), 400

    if 'user_lat' not in data or 'user_lon' not in data:
        return jsonify({
            "status": "error",
            "message": "Необходимо указать user_lat и user_lon"
        }), 400

    try:
        user_lat = float(data['user_lat'])
        user_lon = float(data['user_lon'])
        search_radius = int(data.get('search_radius', 1000))  # по умолчанию 1км

        # Валидация координат
        if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
            return jsonify({
                "status": "error",
                "message": "Неверные координаты пользователя"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Координаты должны быть числами"
        }), 400

    # ШАГ 1: Получаем список парковок от Prague Parking API
    parking_spots = get_parking_spots(user_lat, user_lon, search_radius)

    if not parking_spots:
        return jsonify({
            "status": "error",
            "message": "Не удалось найти парковки в указанном радиусе"
        }), 404

    # ШАГ 2: Находим ближайшую парковку
    closest_parking, distance_to_parking = find_closest_parking(
        user_lat, user_lon, parking_spots
    )

    if not closest_parking:
        return jsonify({
            "status": "error",
            "message": "Не удалось определить ближайшую парковку"
        }), 500

    parking_lat = closest_parking["position"]["lat"]
    parking_lon = closest_parking["position"]["lon"]

    # ШАГ 3: Строим маршрут от пользователя до парковки
    try:
        route_data = build_route(user_lat, user_lon, parking_lat, parking_lon)

        # ШАГ 4: Возвращаем готовый маршрут на фронтенд
        return jsonify({
            "status": "success",
            "user_location": {
                "lat": user_lat,
                "lon": user_lon
            },
            "parking": {
                "position": closest_parking["position"],
                "address": closest_parking["address"],
                "capacity": closest_parking.get("capacity", "N/A"),
                "date": closest_parking.get("date", "N/A"),
                "distance_meters": round(distance_to_parking, 2)
            },
            "route_length_meters": route_data["route_length"],
            "path": route_data["path_coordinates"]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Ошибка построения маршрута: {str(e)}"
        }), 500


# ========== MOCK PARKING API (simulation) ==========
@app.route('/mock-parking-api', methods=['GET'])
def mock_parking_api():
    """
    Симулирует ответ Prague Parking API
    Возвращает несколько тестовых парковок вокруг центра Праги
    """
    data = request.get_json(silent=True)

    # Получаем координаты пользователя из запроса
    user_position = data.get('position', {})
    user_lat = user_position.get('lat', 50.0755)
    user_lon = user_position.get('lon', 14.4378)

    # Возвращаем фейковые парковки вокруг пользователя (в радиусе ~500-800м)
    mock_parkings = [
        {
            "position": {
                "lat": user_lat + 0.005,  # ~550м на север
                "lon": user_lon + 0.003
            },
            "address": {
                "postal_code": "11000",
                "street": "Václavské náměstí",
                "house_number": "12"
            },
            "capacity": 15,
            "date": "2025-12-16T22:00:00"
        },
        {
            "position": {
                "lat": user_lat + 0.008,  # ~880м на север
                "lon": user_lon + 0.002
            },
            "address": {
                "postal_code": "11000",
                "street": "Na Příkopě",
                "house_number": "25"
            },
            "capacity": 8,
            "date": "2025-12-16T22:00:00"
        },
        {
            "position": {
                "lat": user_lat - 0.004,  # ~440м на юг
                "lon": user_lon + 0.006
            },
            "address": {
                "postal_code": "12000",
                "street": "Karlovo náměstí",
                "house_number": "5"
            },
            "capacity": 22,
            "date": "2025-12-16T22:00:00"
        },
        {
            "position": {
                "lat": user_lat + 0.003,
                "lon": user_lon - 0.005
            },
            "address": {
                "postal_code": "11000",
                "street": "Národní třída",
                "house_number": "40"
            },
            "capacity": 5,
            "date": "2025-12-16T22:00:00"
        }
    ]

    print(f"[MOCK API] Возвращаю {len(mock_parkings)} парковок для координат ({user_lat}, {user_lon})")

    return jsonify(mock_parkings), 200


# ========== КОНЕЦ MOCK API ==========











if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
