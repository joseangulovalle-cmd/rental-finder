"""
Scraper para Craigslist Toronto usando RSS feed
"""

import requests
import hashlib
import xml.etree.ElementTree as ET
from math import radians, cos, sin, asin, sqrt
from config import SCHOOL_LAT, SCHOOL_LON, MAX_DISTANCE_KM

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# RSS de Craigslist: apartamentos, 2 cuartos, Toronto
RSS_URL = (
    "https://toronto.craigslist.org/search/apa?format=rss"
    "&min_bedrooms=2&max_bedrooms=2"
    "&lat=43.6802&lon=-79.3959&search_distance=0.75"
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
        response = requests.get(RSS_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()

        # Craigslist RSS usa namespaces propios
        content = response.content.replace(b'xmlns="', b'xmlns:unused="')
        root = ET.fromstring(content)
        items = root.findall(".//item")

        for item in items:
            try:
                title = item.findtext("title", "Sin titulo").strip()
                listing_url = item.findtext("link", "").strip()

                # Precio desde el titulo
                price = "Precio no indicado"
                if "$" in title:
                    import re
                    match = re.search(r'\$[\d,]+', title)
                    if match:
                        price = match.group(0)

                # Coordenadas desde geo
                lat = item.findtext("{http://www.w3.org/2003/01/geo/wgs84_pos#}lat")
                lon = item.findtext("{http://www.w3.org/2003/01/geo/wgs84_pos#}long")

                distance_km = None
                if lat and lon:
                    try:
                        distance_km = round(haversine(float(lat), float(lon), SCHOOL_LAT, SCHOOL_LON), 2)
                        if distance_km > MAX_DISTANCE_KM:
                            continue
                    except Exception:
                        pass

                uid = hashlib.md5(f"craigslist-{listing_url}".encode()).hexdigest()

                listings.append({
                    "id": uid,
                    "title": title,
                    "price": price,
                    "location": "Toronto, ON",
                    "distance_km": distance_km,
                    "image_url": "",
                    "listing_url": listing_url,
                    "source": "Craigslist",
                    "bedrooms": "2",
                    "bathrooms": "—",
                })
            except Exception:
                continue

    except Exception as e:
        print(f"[Craigslist] Error: {e}")

    print(f"[Craigslist] {len(listings)} anuncios encontrados")
    return listings
