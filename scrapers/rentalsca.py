"""
Scraper para Rentals.ca usando Playwright
"""

import hashlib
from playwright.sync_api import sync_playwright
from config import SCHOOL_LAT, SCHOOL_LON, MAX_DISTANCE_KM

URL = "https://rentals.ca/toronto?beds-min=2&lat=43.6802&lng=-79.3959&zoom=14"


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
            page.goto(URL, wait_until="networkidle", timeout=40000)
            page.wait_for_timeout(3000)

            items = page.query_selector_all("div.listing-card, article.listing, div[class*='listing-item']")

            for item in items:
                try:
                    title_el = item.query_selector("h2, h3, [class*='title'], [class*='name']")
                    title = title_el.inner_text().strip() if title_el else "Sin titulo"

                    price_el = item.query_selector("[class*='price'], [class*='rent']")
                    price = price_el.inner_text().strip() if price_el else "Precio no indicado"

                    link_el = item.query_selector("a[href]")
                    listing_url = ""
                    if link_el:
                        href = link_el.get_attribute("href") or ""
                        listing_url = f"https://rentals.ca{href}" if href.startswith("/") else href

                    img_el = item.query_selector("img")
                    image_url = ""
                    if img_el:
                        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src") or ""

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

            browser.close()

    except Exception as e:
        print(f"[Rentals.ca] Error: {e}")

    print(f"[Rentals.ca] {len(listings)} anuncios encontrados")
    return listings
