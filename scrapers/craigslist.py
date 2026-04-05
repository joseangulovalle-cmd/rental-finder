"""
Scraper para Craigslist Toronto usando Playwright
"""

import hashlib
from playwright.sync_api import sync_playwright

URL = (
    "https://toronto.craigslist.org/search/toronto-on/apa"
    "?lat=43.6769&lon=-79.4064"
    "&min_bathrooms=2&max_bathrooms=2"
    "&min_bedrooms=2&max_bedrooms=2"
    "&search_distance=0.8"
)

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
            page.wait_for_timeout(3000)

            # Craigslist nuevo diseno usa li.cl-search-result
            items = page.query_selector_all("li.cl-search-result, li.result-row")
            print(f"[Craigslist] Elementos encontrados en pagina: {len(items)}")

            for item in items:
                try:
                    # Titulo y link
                    title_el = item.query_selector("a.posting-title, a[class*='title'], .title a")
                    title = ""
                    listing_url = ""
                    if title_el:
                        title = title_el.inner_text().strip()
                        listing_url = title_el.get_attribute("href") or ""

                    if not title or not listing_url:
                        continue

                    # Precio
                    price_el = item.query_selector(".priceinfo, .price, [class*='price']")
                    price = price_el.inner_text().strip() if price_el else "Precio no indicado"

                    # Imagen
                    img_el = item.query_selector("img")
                    image_url = img_el.get_attribute("src") or "" if img_el else ""

                    uid = hashlib.md5(f"craigslist-{listing_url}".encode()).hexdigest()

                    listings.append({
                        "id": uid,
                        "title": title,
                        "price": price,
                        "location": "Toronto, ON",
                        "distance_km": None,
                        "image_url": image_url,
                        "listing_url": listing_url,
                        "source": "Craigslist",
                        "bedrooms": "2",
                        "bathrooms": "2",
                    })
                except Exception:
                    continue

            browser.close()

    except Exception as e:
        print(f"[Craigslist] Error: {e}")

    print(f"[Craigslist] {len(listings)} anuncios encontrados")
    return listings
