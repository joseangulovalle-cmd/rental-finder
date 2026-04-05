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
            page.goto(URL, wait_until="networkidle", timeout=40000)
            page.wait_for_timeout(6000)

            # Esperar a que carguen los anuncios
            try:
                page.wait_for_selector('a[href*="/v-"]', timeout=10000)
            except Exception:
                pass

            # Extraer datos via JavaScript directamente en la pagina
            results = page.evaluate("""
                () => {
                    const listings = [];
                    const seen = new Set();

                    // Kijiji: todos los links de anuncios contienen /v- y terminan en numeros
                    const allLinks = Array.from(document.querySelectorAll('a[href]'));

                    allLinks.forEach(link => {
                        const href = link.href || '';
                        // Patron: kijiji.ca/v-algo/ciudad/titulo/NUMERO
                        if (!href.includes('kijiji.ca/v-')) return;
                        if (!href.match(/\\/\\d{10,}/)) return; // ID numerico largo al final
                        if (seen.has(href)) return;
                        seen.add(href);

                        const title = link.innerText.trim();
                        if (!title || title.length < 5) return;

                        // Contenedor del anuncio
                        let container = link.closest('li') ||
                                       link.closest('article') ||
                                       link.closest('[data-listing-id]') ||
                                       link.parentElement?.parentElement;

                        // Precio
                        let price = 'Precio no indicado';
                        if (container) {
                            // Buscar texto con $ en el contenedor
                            const allText = container.innerText || '';
                            const priceMatch = allText.match(/\\$[\\d,]+(\\.\\d{2})?/);
                            if (priceMatch) price = priceMatch[0];
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
