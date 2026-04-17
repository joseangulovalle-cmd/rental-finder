"""
Scraper para Craigslist Toronto usando Playwright
Busca por patron de URL
"""

import hashlib
from playwright.sync_api import sync_playwright

URL = (
    "https://toronto.craigslist.org/search/toronto-on/hhh"
    "?lat=43.6769&lon=-79.4064"
    "&min_bathrooms=2"
    "&min_bedrooms=2&max_bedrooms=3"
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
            page.goto(URL, wait_until="networkidle", timeout=40000)
            page.wait_for_timeout(4000)

            # Cambiar a vista de lista si está en galería
            try:
                list_btn = page.query_selector('button[title="list"], [aria-label="list view"], .cl-list-view')
                if list_btn:
                    list_btn.click()
                    page.wait_for_timeout(2000)
            except Exception:
                pass

            results = page.evaluate("""
                () => {
                    const listings = [];
                    const seen = new Set();

                    // Craigslist: todos los links de anuncios tienen /apa/d/ en la URL
                    const allLinks = Array.from(document.querySelectorAll('a[href]'));

                    allLinks.forEach(link => {
                        const href = link.href || '';
                        if (!href.includes('craigslist.org') ) return;
                        if (!href.includes('/apa/d/') && !href.includes('/hhh/d/') && !href.match(/\\.html$/)) return;
                        if (seen.has(href)) return;
                        seen.add(href);

                        const title = link.innerText.trim();
                        if (!title || title.length < 5) return;

                        let container = link.closest('li') ||
                                       link.closest('article') ||
                                       link.parentElement?.parentElement;

                        let price = 'Precio no indicado';
                        if (container) {
                            const allText = container.innerText || '';
                            const priceMatch = allText.match(/\\$[\\d,]+/);
                            if (priceMatch) price = priceMatch[0];
                        }

                        // Sqft
                        let sqft = null;
                        if (container) {
                            const allText = container.innerText || '';
                            const sqftMatch = allText.match(/(\\d[\\d,]+)\\s*(ft²|sq\\.?\\s*ft\\.?|sqft)/i);
                            if (sqftMatch) sqft = sqftMatch[1].replace(',', '');
                        }

                        let image_url = '';
                        if (container) {
                            const img = container.querySelector('img');
                            if (img) image_url = img.src || '';
                        }

                        // Ubicacion (barrio) — aparece entre parentesis en Craigslist
                        let location = '';
                        if (container) {
                            const hood = container.querySelector('.result-hood, .housing-hood, [class*="hood"], [class*="location"]');
                            if (hood) {
                                location = hood.innerText.replace(/[()]/g, '').trim();
                            } else {
                                // Intentar extraer del texto completo: "(Barrio)"
                                const allText = container.innerText || '';
                                const hoodMatch = allText.match(/\\(([^)]{3,40})\\)/);
                                if (hoodMatch) location = hoodMatch[1].trim();
                            }
                        }

                        listings.push({ href, title, price, sqft, image_url, location });
                    });

                    return listings;
                }
            """)

            print(f"[Craigslist] Elementos encontrados en pagina: {len(results)}")

            for r in results:
                uid = hashlib.md5(f"craigslist-{r['href']}".encode()).hexdigest()
                listings.append({
                    "id": uid,
                    "title": r["title"],
                    "price": r["price"],
                    "location": r.get("location") or "Toronto, ON",
                    "distance_km": None,
                    "image_url": r["image_url"],
                    "listing_url": r["href"],
                    "source": "Craigslist",
                    "bedrooms": "2",
                    "bathrooms": "2",
                    "sqft": r.get("sqft"),
                })

            browser.close()

    except Exception as e:
        print(f"[Craigslist] Error: {e}")

    print(f"[Craigslist] {len(listings)} anuncios encontrados")
    return listings
