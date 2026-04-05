"""
Scraper para Rentals.ca
El sitio mas grande de arriendos en Canada
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
    "Referer": "https://rentals.ca/",
}

# Busqueda: Toronto, 2 cuartos, zona Annex/Casa Loma (donde esta el colegio)
SEARCH_URL = "https://rentals.ca/toronto?beds-min=2&lat=43.6802&lng=-79.3959&zoom=14"


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
        response = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Rentals.ca usa tarjetas con clase listing-card o similar
        items = soup.select("div.listing-card, article.listing, div[class*='listing']")

        for item in items:
            try:
                # Titulo
                title_el = item.select_one("h2, h3, [class*='title'], [class*='name']")
                title = title_el.get_text(strip=True) if title_el else "Sin titulo"

                # Precio
                price_el = item.select_one("[class*='price'], [class*='rent']")
                price = price_el.get_text(strip=True) if price_el else "Precio no indicado"

                # Link
                link_el = item.select_one("a[href]")
                listing_url = ""
                if link_el:
                    href = link_el.get("href", "")
                    listing_url = f"https://rentals.ca{href}" if href.startswith("/") else href

                # Imagen
                img_el = item.select_one("img")
                image_url = ""
                if img_el:
                    image_url = img_el.get("src") or img_el.get("data-src") or ""

                if not listing_url:
                    continue

                uid = hashlib.md5(f"rentalsca-{listing_url}".encode()).hexdigest()

                listings.append({
                    "id": uid,
                    "title": title,
                    "price": price,
                    "location": "Toronto, ON",
                    "distance_km": None,
                    "image_url": image_url,
                    "listing_url": listing_url,
                    "source": "Rentals.ca",
                    "bedrooms": "2",
                    "bathrooms": "—",
                })
            except Exception:
                continue

    except Exception as e:
        print(f"[Rentals.ca] Error: {e}")

    print(f"[Rentals.ca] {len(listings)} anuncios encontrados")
    return listings
