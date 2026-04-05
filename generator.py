"""
Generador de pagina web HTML
Crea index.html con todas las propiedades encontradas
"""

from datetime import datetime
from config import SCHOOL_NAME, OUTPUT_HTML


def generate(listings):
    """Genera la pagina web con todas las propiedades."""

    updated_at = datetime.utcnow().strftime("%B %d, %Y – %H:%M UTC")
    total = len(listings)

    if not listings:
        cards_html = """
        <div style="text-align:center;padding:60px 20px;color:#888;">
            <div style="font-size:60px;">🔍</div>
            <h3>Aun no hay propiedades</h3>
            <p>El buscador revisara los sitios pronto y actualizara esta pagina.</p>
        </div>
        """
    else:
        cards_html = ""
        for lst in listings:
            distance_text = f"🚶 {lst['distance_km']} km del colegio" if lst.get("distance_km") else "📍 Zona cercana"
            image_html = (
                f'<img src="{lst["image_url"]}" alt="Foto propiedad" '
                f'onerror="this.style.display=\'none\'" />'
                if lst.get("image_url") else
                '<div class="no-image">📷 Sin foto</div>'
            )
            source_color = {
                "Kijiji": "#e05b29",
                "Craigslist": "#6c3483",
                "Rentals.ca": "#0e7c5b",
                "Realtor.ca": "#d4171e",
            }.get(lst["source"], "#2563eb")

            cards_html += f"""
            <div class="card">
                <div class="card-image">
                    {image_html}
                    <span class="badge" style="background:{source_color};">{lst['source']}</span>
                </div>
                <div class="card-body">
                    <div class="price">{lst['price']}</div>
                    <h3 class="title">{lst['title']}</h3>
                    <div class="meta">
                        <span>🛏 {lst.get('bedrooms','2')} cuartos</span>
                        <span>🚿 {lst.get('bathrooms','—')} baños</span>
                    </div>
                    <div class="location">📍 {lst['location']}</div>
                    <div class="distance">{distance_text}</div>
                    <a href="{lst['listing_url']}" target="_blank" class="btn">
                        Ver anuncio →
                    </a>
                </div>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Arriendos cerca de Waldorf Academy — Toronto</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f0f4f8;
            color: #1a202c;
        }}

        header {{
            background: linear-gradient(135deg, #1e3a5f, #2563eb);
            color: white;
            padding: 24px 20px;
            text-align: center;
        }}
        header h1 {{ font-size: 1.6rem; margin-bottom: 6px; }}
        header p  {{ opacity: 0.85; font-size: 0.95rem; }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 16px 20px;
            background: white;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9rem;
            color: #555;
            flex-wrap: wrap;
        }}
        .stats strong {{ color: #2563eb; font-size: 1.1rem; }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 24px auto;
            padding: 0 16px;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}

        .card-image {{ position: relative; height: 200px; background: #e2e8f0; overflow: hidden; }}
        .card-image img {{ width: 100%; height: 100%; object-fit: cover; }}
        .no-image {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #a0aec0;
        }}

        .badge {{
            position: absolute;
            top: 12px;
            left: 12px;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}

        .card-body {{ padding: 16px; }}
        .price {{ font-size: 1.5rem; font-weight: 700; color: #16a34a; margin-bottom: 6px; }}
        .title {{ font-size: 0.95rem; color: #2d3748; margin-bottom: 10px; line-height: 1.4; }}
        .meta {{ display: flex; gap: 12px; font-size: 0.85rem; color: #718096; margin-bottom: 8px; }}
        .location {{ font-size: 0.85rem; color: #718096; margin-bottom: 4px; }}
        .distance {{ font-size: 0.85rem; color: #2563eb; font-weight: 500; margin-bottom: 14px; }}

        .btn {{
            display: block;
            text-align: center;
            background: #2563eb;
            color: white;
            padding: 10px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #1d4ed8; }}

        footer {{
            text-align: center;
            padding: 30px;
            color: #a0aec0;
            font-size: 0.8rem;
        }}

        @media (max-width: 640px) {{
            header h1 {{ font-size: 1.2rem; }}
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

<header>
    <h1>🏠 Arriendos cerca de Waldorf Academy</h1>
    <p>250 Madison Ave, Toronto · 2 cuartos · Radio 1.2 km (~15 min a pie)</p>
</header>

<div class="stats">
    <span><strong>{total}</strong> propiedades encontradas</span>
    <span>Fuentes: Kijiji · Craigslist · Realtor.ca</span>
    <span>Actualizado: {updated_at}</span>
</div>

<div class="grid">
    {cards_html}
</div>

<footer>
    Buscador privado para la familia Angulo · Haz click en cualquier propiedad para ver el anuncio original
</footer>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Web] Pagina generada con {total} propiedades → {OUTPUT_HTML}")
