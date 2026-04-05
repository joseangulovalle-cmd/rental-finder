"""
Scraper para Kijiji.ca usando Playwright
Navega como un humano real para evitar bloqueos
"""

import hashlib
import re
from math import radians, cos, sin, asin, sqrt
from playwright.sync_api import sync_playwright
from config import SCHOOL_LAT, SCHOOL_LON, MAX_DISTANCE_KM

URL = (
    "https://www.kijiji.ca/b-apartments-condos/toronto/"
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

            items = page.query_selector_all("li[data-listing-id], div[data-listing-id]")

            for item in items:
                try:
                    listing_id = item.get_attribute("data-listing-id") or ""

                    title_el = item.query_selector("[class*='title']")
                    title = title_el.inner_text().strip() if title_el else "Sin titulo"

                    price_el = item.query_selector("[class*='price']")
                    price = price_el.inner_text().strip() if price_el else "Precio no indicado"

                    link_el = item.query_selector("a[href*='/v-']")
                    listing_url = ""
                    if link_el:
                        href = link_el.get_attribute("href") or ""
                        listing_url = f"https://www.kijiji.ca{href}" if href.startswith("/") else href

                    img_el = item.query_selector("img")
                    image_url = ""
                    if img_el:
                        image_url = img_el.get_attribute("data-src") or img_el.get_attribute("src") or ""

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

                    uid = hashlib.md5(f"kijiji-{listing_id or listing_url}".encode()).hexdigest()

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

            browser.close()

    except Exception as e:
        print(f"[Kijiji] Error: {e}")

    print(f"[Kijiji] {len(listings)} anuncios encontrados")
    return listings
