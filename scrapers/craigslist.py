"""
Scraper para Craigslist Toronto usando Playwright
"""

import hashlib
import re
from math import radians, cos, sin, asin, sqrt
from playwright.sync_api import sync_playwright
from config import SCHOOL_LAT, SCHOOL_LON, MAX_DISTANCE_KM

URL = (
    "https://toronto.craigslist.org/search/apa"
    "?min_bedrooms=2&max_bedrooms=2"
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
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            items = page.query_selector_all("li.cl-search-result, li.result-row")

            for item in items:
                try:
                    listing_id = item.get_attribute("data-pid") or item.get_attribute("id") or ""

                    title_el = item.query_selector("a.posting-title, a.result-title")
                    title = "Sin titulo"
                    listing_url = ""
                    if title_el:
                        title = title_el.inner_text().strip()
                        listing_url = title_el.get_attribute("href") or ""

                    price_el = item.query_selector(".priceinfo, .result-price")
                    price = price_el.inner_text().strip() if price_el else "Precio no indicado"

                    lat = item.get_attribute("data-latitude")
                    lon = item.get_attribute("data-longitude")
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

            browser.close()

    except Exception as e:
        print(f"[Craigslist] Error: {e}")

    print(f"[Craigslist] {len(listings)} anuncios encontrados")
    return listings
