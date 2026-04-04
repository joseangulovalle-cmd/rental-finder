"""
Scraper para Craigslist Toronto
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
}

# URL de Craigslist: apartamentos, 2 cuartos, radio 0.75 millas (~1.2 km) de Madison Ave
CRAIGSLIST_URL = (
    "https://toronto.craigslist.org/search/apa"
    "?min_bedrooms=2&max_bedrooms=2"
    "&lat=43.6802&lon=-79.3959&search_distance=0.75"
    "&availabilityMode=0&sale_date=all+dates"
)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


def scrape():
    listings = []
    try:
        response = requests.get(CRAIGSLIST_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Craigslist usa <li class="cl-search-result"> o <li class="result-row">
        items = soup.select("li.cl-search-result, li.result-row")

        for item in items:
            try:
                # ID unico del anuncio
                listing_id = item.get("data-pid", "") or item.get("id", "")

                # Titulo y link
                title_el = item.select_one("a.posting-title, a.result-title")
                title = "Sin titulo"
                listing_url = ""
                if title_el:
                    title = title_el.get_text(strip=True)
                    listing_url = title_el.get("href", "")
                    if listing_url and not listing_url.startswith("http"):
                        listing_url = f"https://toronto.craigslist.org{listing_url}"

                # Precio
                price_el = item.select_one(".priceinfo, .result-price")
                price = price_el.get_text(strip=True) if price_el else "Precio no indicado"

                # Ubicacion
                loc_el = item.select_one(".meta, .result-hood, .maptag")
                location = loc_el.get_text(strip=True) if loc_el else "Toronto, ON"
                location = location.strip("() ")

                # Imagen (Craigslist usa swipe gallery)
                img_el = item.select_one("img")
                image_url = ""
                if img_el:
                    image_url = img_el.get("src") or ""

                # Coordenadas
                lat = item.get("data-latitude")
                lon = item.get("data-longitude")

                distance_km = None
                if lat and lon:
                    try:
                        distance_km = round(haversine(float(lat), float(lon), SCHOOL_LAT, SCHOOL_LON), 2)
                        if distance_km > MAX_DISTANCE_KM:
                            continue
                    except Exception:
                        pass

                uid = hashlib.md5(f"craigslist-{listing_id or listing_url}".encode()).hexdigest()

                listings.append({
                    "id": uid,
                    "title": title,
                    "price": price,
                    "location": location if location else "Toronto, ON",
                    "distance_km": distance_km,
                    "image_url": image_url,
                    "listing_url": listing_url,
                    "source": "Craigslist",
                    "bedrooms": "2",
                    "bathrooms": "—",
                })
            except Exception:
                continue

    except Exception as e:
        print(f"[Craigslist] Error al scrapear: {e}")

    print(f"[Craigslist] {len(listings)} anuncios encontrados")
    return listings
