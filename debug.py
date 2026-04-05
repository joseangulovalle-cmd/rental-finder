"""
Script de diagnostico - toma fotos de pantalla de lo que ve el bot
en cada sitio para comparar con la busqueda manual
"""

import os
from playwright.sync_api import sync_playwright

SITES = [
    {
        "name": "kijiji",
        "url": (
            "https://www.kijiji.ca/b-apartments-condos/city-of-toronto/"
            "2+bathrooms-2+bedrooms/c37l1700273a120a27949001"
            "?address=Toronto%2C%20ON%20M4V%202W6"
            "&ll=43.67720569999999%2C-79.40699769999999"
            "&radius=2.0&view=list"
        ),
        "wait": 4000,
    },
    {
        "name": "craigslist",
        "url": (
            "https://toronto.craigslist.org/search/toronto-on/apa"
            "?lat=43.6769&lon=-79.4064"
            "&min_bathrooms=2&max_bathrooms=2"
            "&min_bedrooms=2&max_bedrooms=2"
            "&search_distance=0.8"
        ),
        "wait": 3000,
    },
    {
        "name": "rentalsca",
        "url": "https://rentals.ca/toronto?baths=2&h3=872b9bc73ffffff",
        "wait": 5000,
    },
    {
        "name": "realtorca",
        "url": (
            "https://www.realtor.ca/map#ZoomLevel=16"
            "&Center=43.677156%2C-79.407009"
            "&LatitudeMax=43.67976&LongitudeMax=-79.39628"
            "&LatitudeMin=43.67455&LongitudeMin=-79.41774"
            "&Sort=6-D&PropertyTypeGroupID=1&TransactionTypeId=3"
            "&PropertySearchTypeId=0&BedRange=2-2&BathRange=2-2&Currency=CAD"
        ),
        "wait": 7000,
    },
]

os.makedirs("screenshots", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    for site in SITES:
        print(f"\n[{site['name'].upper()}] Abriendo pagina...")
        page = browser.new_page(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        try:
            page.goto(site["url"], wait_until="domcontentloaded", timeout=40000)
            page.wait_for_timeout(site["wait"])
            screenshot_path = f"screenshots/{site['name']}.png"
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"[{site['name'].upper()}] Foto guardada: {screenshot_path}")
        except Exception as e:
            print(f"[{site['name'].upper()}] Error: {e}")
        finally:
            page.close()

    browser.close()

print("\nListo! Fotos guardadas en carpeta screenshots/")
