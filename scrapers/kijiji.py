"""
Scraper para Kijiji.ca usando Playwright
Busca por patron de URL en lugar de clases CSS
"""

import hashlib
from playwright.sync_api import sync_playwright

URL = (
    "https://www.kijiji.ca/b-apartments-condos/city-of-toronto/"
    "2+bathrooms-2+bedrooms/c37l1700273a120a27949001"
    "?address=Toronto%2C%20ON%20M4V%202W6"
    "&ll=43.67720569999999%2C-79.40699769999999"
    "&radius=2.0&view=list"
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
            page.wait_for_timeout(5000)

            # Extraer datos via JavaScript directamente en la pagina
            results = page.evaluate("""
                () => {
                    const listings = [];
                    // Buscar todos los links que sean anuncios de Kijiji (/v- es el patron de listings)
                    const links = document.querySelectorAll('a[href*="/v-"]');
                    const seen = new Set();

                    links.forEach(link => {
                        const href = link.href;
                        // Filtrar solo links de anuncios reales (tienen numeros al final)
                        if (!href.match(/\\/v-[\\w-]+\\/\\d+/) ) return;
                        if (seen.has(href)) return;
                        seen.add(href);

                        // Subir en el DOM para encontrar el contenedor del anuncio
                        let container = link.closest('li') || link.closest('article') || link.parentElement;

                        // Titulo
                        const title = link.innerText.trim() || link.title || '';
                        if (!title || title.length < 5) return;

                        // Precio — buscar en el contenedor
                        let price = 'Precio no indicado';
                        if (container) {
                            const priceEl = container.querySelector('[class*="price"], [data-testid*="price"]');
                            if (priceEl) price = priceEl.innerText.trim();
                        }

                        // Imagen
                        let image_url = '';
                        if (container) {
                            const img = container.querySelector('img');
                            if (img) image_url = img.src || img.dataset.src || '';
                        }

                        listings.push({ href, title, price, image_url });
                    });

                    return listings;
                }
            """)

            print(f"[Kijiji] Elementos encontrados en pagina: {len(results)}")

            for r in results:
                uid = hashlib.md5(f"kijiji-{r['href']}".encode()).hexdigest()
                listings.append({
                    "id": uid,
                    "title": r["title"],
                    "price": r["price"],
                    "location": "Toronto, ON",
                    "distance_km": None,
                    "image_url": r["image_url"],
                    "listing_url": r["href"],
                    "source": "Kijiji",
                    "bedrooms": "2",
                    "bathrooms": "2",
                })

            browser.close()

    except Exception as e:
        print(f"[Kijiji] Error: {e}")

    print(f"[Kijiji] {len(listings)} anuncios encontrados")
    return listings
