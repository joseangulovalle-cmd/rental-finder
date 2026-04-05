"""
Geocoder usando OpenStreetMap (Nominatim) - 100% gratis
Convierte direcciones de texto a coordenadas GPS
y calcula distancias a puntos de interes
"""

import requests
import time
from math import radians, cos, sin, asin, sqrt

# Coordenadas fijas
SCHOOL_LAT  = 43.6772
SCHOOL_LON  = -79.4071
SCHOOL_NAME = "Waldorf Academy"

DUPONT_STATION_LAT = 43.6747
DUPONT_STATION_LON = -79.4064
DUPONT_STATION_NAME = "Dupont Station (Subway)"

HEADERS = {
    "User-Agent": "rental-finder-family-app/1.0 (jose.angulo.valle@gmail.com)"
}


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos GPS."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return round(R * 2 * asin(sqrt(a)), 2)


def km_to_walk_minutes(km):
    """Convierte km a minutos caminando (velocidad promedio 4.5 km/h)."""
    return round((km / 4.5) * 60)


def geocode_address(address):
    """
    Convierte una direccion de texto a coordenadas GPS.
    Usa OpenStreetMap Nominatim - gratis, sin API key.
    """
    try:
        # Limpiar la direccion
        clean = address.replace("|", ", ").strip()
        if "Toronto" not in clean:
            clean += ", Toronto, Ontario, Canada"

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": clean,
            "format": "json",
            "limit": 1,
            "countrycodes": "ca",
        }
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon

    except Exception:
        pass

    return None, None


def looks_like_address(text):
    """Verifica si el texto parece una direccion real (tiene numero y calle)."""
    import re
    # Una direccion real tiene numeros seguidos de nombre de calle
    return bool(re.search(r'\d+\s+\w+', text)) and len(text) > 10


def enrich_listing(listing):
    """
    Agrega distancias al colegio y al subway a un anuncio.
    Si ya tiene coordenadas, las usa. Si no, geocodifica la direccion.
    """
    lat = listing.get("lat")
    lon = listing.get("lon")

    # Si no tiene coordenadas, intentar geocodificar
    if not lat or not lon:
        # Preferir el titulo de Realtor.ca (siempre es una direccion real)
        # Para Kijiji/Craigslist solo intentar si parece una direccion
        source = listing.get("source", "")
        address = listing.get("location", "") or listing.get("title", "")

        should_geocode = (
            source == "Realtor.ca" or
            (address and address != "Toronto, ON" and looks_like_address(address))
        )

        if should_geocode:
            lat, lon = geocode_address(address)
            time.sleep(1)  # Respetar limite de OpenStreetMap (1 req/seg)

    if lat and lon:
        # Distancia al colegio
        dist_school = haversine(lat, lon, SCHOOL_LAT, SCHOOL_LON)
        mins_school = km_to_walk_minutes(dist_school)

        # Distancia a Dupont Station
        dist_subway = haversine(lat, lon, DUPONT_STATION_LAT, DUPONT_STATION_LON)
        mins_subway = km_to_walk_minutes(dist_subway)

        listing["distance_km"] = dist_school
        listing["walk_minutes_school"] = mins_school
        listing["distance_subway_km"] = dist_subway
        listing["walk_minutes_subway"] = mins_subway
        listing["lat"] = lat
        listing["lon"] = lon
    else:
        listing["distance_km"] = None
        listing["walk_minutes_school"] = None
        listing["distance_subway_km"] = None
        listing["walk_minutes_subway"] = None

    return listing
