"""
Scraper para Kijiji.ca usando Playwright
"""

import hashlib
from playwright.sync_api import sync_playwright
from config import SCHOOL_LAT, SCHOOL_LON, MAX_DISTANCE_KM
from math import radians, cos, sin, asin, sqrt

URL = (
    "https://www.kijiji.ca/b-apartments-condos/city-of-toronto/"
    "2+bathrooms-2+bedrooms/c37l1700273a120a27949001"
    "?address=Toronto%2C%20ON%20M4V%202W6"
    "&ll=43.67720569999999%2C-79.40699769999999"
    "&radius=2.0&view=list"
)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

def scrape():
    listings = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1280, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)

            # Kijiji lista los anuncios en elementos <li> con atributo data-listing-id
            # o en divs con clase que contiene "regular-ad"
            items = page.query_selector_all(
                "li[data-listing-id], "
                "div[data-listing-id], "
                "[class*='regular-ad'], "
                "[class*='search-item']"
            )

            print(f"[Kijiji] Elementos encontrados en pagina: {len(items)}")

            for item in items:
                try:
                    listing_id = (
                        item.get_attribute("data-listing-id") or
                        item.get_attribute("id") or ""
                    )

                    # Titulo y link — Kijiji usa <a> con el titulo dentro
                    title_el = item.query_selector("a[class*='title'], h3 a, [data-testid*='title'] a, a[href*='/v-']")
                    title = title_el.inner_text().strip() if title_el else ""
                    listing_url = ""
                    if title_el:
                        href = title_el.get_attribute("href") or ""
                        listing_url = f"https://www.kijiji.ca{href}" if href.startswith("/") else href

                    if not title or not listing_url:
                        continue

                    # Precio
                    price_el = item.query_selector("[class*='price'], [data-testid*='price']")
                    price = price_el.inner_text().strip() if price_el else "Precio no indicado"

                    # Imagen
                    img_el = item.query_selector("img")
                    image_url = ""
                    if img_el:
                        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src") or ""

                    uid = hashlib.md5(f"kijiji-{listing_id or listing_url}".encode()).hexdigest()

                    listings.append({
                        "id": uid,
                        "title": title,
                        "price": price,
                        "location": "Toronto, ON",
                        "distance_km": None,
                        "image_url": image_url,
                        "listing_url": listing_url,
                        "source": "Kijiji",
                        "bedrooms": "2",
                        "bathrooms": "2",
                    })
                except Exception:
                    continue

            browser.close()

    except Exception as e:
        print(f"[Kijiji] Error: {e}")

    print(f"[Kijiji] {len(listings)} anuncios encontrados")
    return listings
