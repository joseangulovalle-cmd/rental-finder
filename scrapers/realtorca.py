"""
Scraper para Realtor.ca usando Playwright
Solo arriendos, 2 cuartos, 2 baños, zona Waldorf Academy
"""

import hashlib
from playwright.sync_api import sync_playwright

# URL con los filtros exactos de la busqueda manual
URL = (
    "https://www.realtor.ca/map#ZoomLevel=16"
    "&Center=43.677156%2C-79.407009"
    "&LatitudeMax=43.67976&LongitudeMax=-79.39628"
    "&LatitudeMin=43.67455&LongitudeMin=-79.41774"
    "&Sort=6-D&PropertyTypeGroupID=1&TransactionTypeId=3"
    "&PropertySearchTypeId=0&BedRange=2-2&BathRange=2-2&Currency=CAD"
)


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
            page.goto(URL, wait_until="domcontentloaded", timeout=40000)
            page.wait_for_timeout(5000)

            items = page.query_selector_all(
                "div.cardCon, div[class*='listing'], div[class*='card'], article"
            )

            for item in items:
                try:
                    title_el = item.query_selector(
                        "[class*='title'], [class*='address'], h2, h3"
                    )
                    title = title_el.inner_text().strip() if title_el else "Sin titulo"

                    price_el = item.query_selector(
                        "[class*='price'], [class*='Price']"
                    )
                    price = price_el.inner_text().strip() if price_el else "Precio no indicado"

                    link_el = item.query_selector("a[href]")
                    listing_url = ""
                    if link_el:
                        href = link_el.get_attribute("href") or ""
                        listing_url = f"https://www.realtor.ca{href}" if href.startswith("/") else href

                    img_el = item.query_selector("img")
                    image_url = ""
                    if img_el:
                        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src") or ""

                    if not listing_url or not title or title == "Sin titulo":
                        continue

                    uid = hashlib.md5(f"realtorca-{listing_url}".encode()).hexdigest()

                    listings.append({
                        "id": uid,
                        "title": title,
                        "price": price,
                        "location": "Toronto, ON",
                        "distance_km": None,
                        "image_url": image_url,
                        "listing_url": listing_url,
                        "source": "Realtor.ca",
                        "bedrooms": "2",
                        "bathrooms": "2",
                    })
                except Exception:
                    continue

            browser.close()

    except Exception as e:
        print(f"[Realtor.ca] Error: {e}")

    print(f"[Realtor.ca] {len(listings)} anuncios encontrados")
    return listings
