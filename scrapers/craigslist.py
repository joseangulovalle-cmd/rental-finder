"""
Scraper para Craigslist Toronto usando Playwright
Busca por patron de URL
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
            page.wait_for_timeout(4000)

            results = page.evaluate("""
                () => {
                    const listings = [];
                    const seen = new Set();

                    // Craigslist: links de anuncios terminan en numeros .html
                    const links = document.querySelectorAll('a.posting-title, a[href*="/apa/d/"]');

                    links.forEach(link => {
                        const href = link.href;
                        if (!href || seen.has(href)) return;
                        seen.add(href);

                        const title = link.innerText.trim() ||
                                      link.querySelector('.label, .titlestring')?.innerText.trim() || '';
                        if (!title || title.length < 5) return;

                        let container = link.closest('li') || link.parentElement;

                        let price = 'Precio no indicado';
                        if (container) {
                            const priceEl = container.querySelector('.priceinfo, .price, [class*="price"]');
                            if (priceEl) price = priceEl.innerText.trim();
                        }

                        let image_url = '';
                        if (container) {
                            const img = container.querySelector('img');
                            if (img) image_url = img.src || '';
                        }

                        listings.push({ href, title, price, image_url });
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
                    "location": "Toronto, ON",
                    "distance_km": None,
                    "image_url": r["image_url"],
                    "listing_url": r["href"],
                    "source": "Craigslist",
                    "bedrooms": "2",
                    "bathrooms": "2",
                })

            browser.close()

    except Exception as e:
        print(f"[Craigslist] Error: {e}")

    print(f"[Craigslist] {len(listings)} anuncios encontrados")
    return listings
