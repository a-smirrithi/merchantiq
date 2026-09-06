import requests
from functools import lru_cache

CITY_COORDS = {
    "Chennai": (13.0827, 80.2707),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Coimbatore": (11.0168, 76.9558),
}

WEATHER_LABELS = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Rain showers", 82: "Heavy showers", 95: "Thunderstorm",
    96: "Thunderstorm + hail", 99: "Severe thunderstorm"
}

@lru_cache(maxsize=16)
def get_weather(city: str):
    lat, lon = CITY_COORDS[city]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    x = r.json()["current"]
    return {
        "temperature": float(x["temperature_2m"]),
        "precipitation": float(x["precipitation"]),
        "weather_code": int(x["weather_code"]),
        "wind_speed": float(x["wind_speed_10m"]),
        "label": WEATHER_LABELS.get(int(x["weather_code"]), "Weather event"),
    }

@lru_cache(maxsize=1)
def get_products():
    # Public product catalog API. Used only as an external live product catalogue.
    url = "https://fakestoreapi.com/products"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data[:12]
