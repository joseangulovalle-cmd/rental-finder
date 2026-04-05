"""
Script de diagnostico - muestra el HTML real de cada sitio
para identificar los selectores correctos
"""

from playwright.sync_api import sync_playwright

def debug_site(name, url, wait=3000):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(wait)
            html = page.content()
            # Mostrar primeros 3000 caracteres del body
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            body = soup.find("body")
            text = body.get_text(separator="\n", strip=True) if body else ""
            print(text[:2000])
            print(f"\n--- Clases de divs principales ---")
            divs = soup.find_all(["div","li","article"], limit=30)
            classes_seen = set()
            for d in divs:
                cls = " ".join(d.get("class", []))
                if cls and cls not in classes_seen:
                    classes_seen.add(cls)
                    print(f"  <{d.name}> class='{cls}'")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

debug_site("KIJIJI", "https://www.kijiji.ca/b-apartments-condos/toronto/2-bedroom/__2-bedrooms/k0c37l1700273a29276001")
debug_site("CRAIGSLIST", "https://toronto.craigslist.org/search/apa?min_bedrooms=2&max_bedrooms=2&lat=43.6802&lon=-79.3959&search_distance=0.75")
debug_site("RENTALS.CA", "https://rentals.ca/toronto?beds-min=2&lat=43.6802&lng=-79.3959&zoom=14", wait=5000)
