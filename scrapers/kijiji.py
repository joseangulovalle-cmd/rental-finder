"""
Scraper para Kijiji.ca usando RSS feed
Mucho mas estable que leer el HTML de la pagina
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

# RSS de Kijiji: apartamentos en renta, 2 cuartos, Toronto
RSS_URL = (
    "https://www.kijiji.ca/rss-srp-apartments-condos/toronto/"
    "2-bedroom/__2-bedrooms/k0c37l1700273a29276001"
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

        root = ET.fromstring(response.content)
        ns = {"media": "http://search.yahoo.com/mrss/"}
        items = root.findall(".//item")

        for item in items:
            try:
                title = item.findtext("title", "Sin titulo").strip()
                listing_url = item.findtext("link", "").strip()
                description = item.findtext("description", "")

                # Precio — suele estar en el titulo o descripcion
                price = "Precio no indicado"
                if "$" in title:
                    parts = title.split("$")
                    if len(parts) > 1:
                        price = "$" + parts[1].split()[0].replace(",", "").strip()
                        price = f"${price.replace('$','')}"

                # Ubicacion
                location_el = item.find(".//{http://www.w3.org/2003/01/geo/wgs84_pos#}Point")
                lat = item.findtext("{http://www.w3.org/2003/01/geo/wgs84_pos#}lat")
                lon = item.findtext("{http://www.w3.org/2003/01/geo/wgs84_pos#}long")

                # Imagen
                img_el = item.find("media:content", ns)
                image_url = ""
                if img_el is not None:
                    image_url = img_el.get("url", "")

                # Calcular distancia
                distance_km = None
                if lat and lon:
                    try:
                        distance_km = round(haversine(float(lat), float(lon), SCHOOL_LAT, SCHOOL_LON), 2)
                        if distance_km > MAX_DISTANCE_KM:
                            continue
                    except Exception:
                        pass

                uid = hashlib.md5(f"kijiji-{listing_url}".encode()).hexdigest()

                listings.append({
                    "id": uid,
                    "title": title,
                    "price": price,
                    "location": "Toronto, ON",
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
        print(f"[Kijiji] Error: {e}")

    print(f"[Kijiji] {len(listings)} anuncios encontrados")
    return listings
