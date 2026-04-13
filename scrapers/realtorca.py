"""
Scraper para Realtor.ca usando Playwright
Intercepta la API de datos directamente
"""

import hashlib
import json
from playwright.sync_api import sync_playwright

# URL de busqueda en vista lista
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
    captured_data = []

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

            # Interceptar respuestas de la API de Realtor.ca
            def handle_response(response):
                if "propertySearch" in response.url or "Search" in response.url:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and "Results" in data:
                            captured_data.extend(data["Results"])
                    except Exception:
                        pass

            page.on("response", handle_response)

            page.goto(URL, wait_until="domcontentloaded", timeout=40000)
            page.wait_for_timeout(6000)

            print(f"[Realtor.ca] Datos de API capturados: {len(captured_data)} propiedades")

            # Si la API funcionó, usar esos datos
            if captured_data:
                for prop in captured_data:
                    try:
                        mls = prop.get("MlsNumber", "")
                        address = prop.get("Property", {}).get("Address", {})
                        full_address = address.get("AddressText", "Toronto, ON")
                        price_raw = prop.get("Property", {}).get("Price", "Precio no indicado")
                        beds = prop.get("Building", {}).get("Bedrooms", "2")
                        baths = prop.get("Building", {}).get("BathroomTotal", "2")
                        photo = prop.get("Property", {}).get("Photo", [{}])
                        image_url = photo[0].get("HighResPath", "") if photo else ""
                        listing_url = f"https://www.realtor.ca{prop.get('RelativeDetailsURL', '')}"

                        # Sqft (puede venir como "750 - 800 sqft" o "750 sqft")
                        size_raw = prop.get("Building", {}).get("SizeInterior", "") or ""
                        sqft = None
                        if size_raw:
                            import re as _re
                            m = _re.search(r"(\d[\d,]*)", str(size_raw))
                            if m:
                                sqft = m.group(1).replace(",", "")

                        # Coordenadas GPS directamente de la API
                        prop_lat = prop.get("Property", {}).get("Address", {}).get("Latitude") or \
                                   prop.get("Building", {}).get("StoriesTotal") and None or \
                                   None
                        # Intentar extraer lat/lon del objeto
                        try:
                            prop_lat = float(prop["Property"]["Address"].get("Latitude", 0)) or None
                            prop_lon = float(prop["Property"]["Address"].get("Longitude", 0)) or None
                        except Exception:
                            prop_lat = None
                            prop_lon = None

                        uid = hashlib.md5(f"realtorca-{mls}".encode()).hexdigest()
                        listings.append({
                            "id": uid,
                            "title": full_address,
                            "price": price_raw,
                            "location": full_address,
                            "distance_km": None,
                            "image_url": image_url,
                            "listing_url": listing_url,
                            "source": "Realtor.ca",
                            "bedrooms": str(beds),
                            "bathrooms": str(baths),
                            "lat": prop_lat,
                            "lon": prop_lon,
                            "sqft": sqft,
                        })
                    except Exception:
                        continue
            else:
                # Fallback: buscar links en la pagina
                results = page.evaluate("""
                    () => {
                        const links = document.querySelectorAll('a[href*="/real-estate/"]');
                        const seen = new Set();
                        const out = [];
                        links.forEach(link => {
                            if (seen.has(link.href)) return;
                            seen.add(link.href);
                            const title = link.innerText.trim();
                            if (title.length < 5) return;
                            out.push({ href: link.href, title });
                        });
                        return out;
                    }
                """)
                print(f"[Realtor.ca] Links encontrados como fallback: {len(results)}")
                for r in results:
                    uid = hashlib.md5(f"realtorca-{r['href']}".encode()).hexdigest()
                    listings.append({
                        "id": uid,
                        "title": r["title"],
                        "price": "Ver en Realtor.ca",
                        "location": "Toronto, ON",
                        "distance_km": None,
                        "image_url": "",
                        "listing_url": r["href"],
                        "source": "Realtor.ca",
                        "bedrooms": "2",
                        "bathrooms": "2",
                    })

            browser.close()

    except Exception as e:
        print(f"[Realtor.ca] Error: {e}")

    print(f"[Realtor.ca] {len(listings)} anuncios encontrados")
    return listings
