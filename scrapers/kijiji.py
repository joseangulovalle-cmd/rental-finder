"""
Scraper para Kijiji.ca
Busca arriendos de 2 cuartos cerca de 250 Madison Ave, Toronto
"""

import requests
from bs4 import BeautifulSoup
import hashlib
from math import radians, cos, sin, asin, sqrt
from config import SCHOOL_LAT, SCHOOL_LON, MAX_DISTANCE_KM

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-CA,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# URL de Kijiji: apartamentos en renta, 2 cuartos, radio 1km de Madison Ave
KIJIJI_URL = (
    "https://www.kijiji.ca/b-for-rent/toronto/k0c37l1700273"
    "?numBedrooms=3"          # numBedrooms=3 en Kijiji = 2 habitaciones
    "&address=250+Madison+Ave%2C+Toronto+ON"
    "&ll=43.6802%2C-79.3959"
    "&radius=1.0"
)


def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos puntos GPS."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


def scrape():
    listings = []
    try:
        response = requests.get(KIJIJI_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Kijiji envuelve cada anuncio en un <li> con data-listing-id
        items = soup.select("li[data-listing-id]")

        for item in items:
            try:
                listing_id = item.get("data-listing-id", "")

                # Titulo
                title_el = item.select_one("[class*='title']")
                title = title_el.get_text(strip=True) if title_el else "Sin titulo"

                # Precio
                price_el = item.select_one("[class*='price']")
                price = price_el.get_text(strip=True) if price_el else "Precio no indicado"

                # Ubicacion
                loc_el = item.select_one("[class*='location']")
                location = loc_el.get_text(strip=True) if loc_el else "Toronto, ON"

                # Imagen
                img_el = item.select_one("img")
                image_url = ""
                if img_el:
                    image_url = img_el.get("data-src") or img_el.get("src") or ""

                # Link al anuncio original
                link_el = item.select_one("a[href*='/v-']")
                listing_url = ""
                if link_el:
                    href = link_el.get("href", "")
                    listing_url = f"https://www.kijiji.ca{href}" if href.startswith("/") else href

                # Coordenadas del anuncio (si Kijiji las incluye)
                lat = item.get("data-latitude")
                lon = item.get("data-longitude")

                distance_km = None
                if lat and lon:
                    try:
                        distance_km = round(haversine(float(lat), float(lon), SCHOOL_LAT, SCHOOL_LON), 2)
                        if distance_km > MAX_DISTANCE_KM:
                            continue  # Demasiado lejos, saltamos
                    except Exception:
                        pass

                uid = hashlib.md5(f"kijiji-{listing_id or listing_url}".encode()).hexdigest()

                listings.append({
                    "id": uid,
                    "title": title,
                    "price": price,
                    "location": location,
                    "distance_km": distance_km,
                    "image_url": image_url,
                    "listing_url": listing_url,
                    "source": "Kijiji",
                    "bedrooms": "2",
                    "bathrooms": "—",
                })
            except Exception:
                continue

    except Exception as e:
        print(f"[Kijiji] Error al scrapear: {e}")

    print(f"[Kijiji] {len(listings)} anuncios encontrados")
    return listings
