"""
Buscador de Arriendos - Toronto
================================
Este archivo es el "director de orquesta":
1. Llama a los scrapers (Kijiji, Craigslist)
2. Compara con anuncios ya vistos
3. Envia email si hay propiedades nuevas
4. Actualiza la pagina web
"""

import json
import os
import re
from datetime import datetime

from scrapers import kijiji, craigslist, realtorca
from geocoder import enrich_listing
from notifier import send_notification
from generator import generate
from config import SEEN_FILE, MAX_PRICE, MIN_SQFT


def _parse_price(price_str):
    """Extrae numero de un string como '$2,500', '2500' o '$3,500/month'. Retorna None si no hay precio."""
    if not price_str or price_str in ("Precio no indicado", "Ver en Realtor.ca"):
        return None
    s = str(price_str)
    # Primero intentar con signo $
    m = re.search(r"\$([\d,]+)", s)
    if m:
        return int(m.group(1).replace(",", ""))
    # Si no hay $, buscar cualquier numero (ej: API de Realtor.ca devuelve "2200")
    m = re.search(r"(\d[\d,]+)", s)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def _parse_sqft(sqft_val):
    """Extrae numero de sqft. Retorna None si no hay dato."""
    if not sqft_val:
        return None
    m = re.search(r"(\d+)", str(sqft_val))
    return int(m.group(1)) if m else None


def meets_filters(listing):
    """Retorna True solo si el anuncio cumple los filtros de precio y sqft.

    Realtor.ca: solo exige precio (sqft no siempre viene en la API de busqueda).
    Kijiji / Craigslist: exige precio y sqft (aparece en la tarjeta del anuncio).
    """
    price = _parse_price(listing.get("price"))
    sqft = _parse_sqft(listing.get("sqft"))
    source = listing.get("source", "")

    if price is None:
        return False   # Sin precio → siempre descartar

    if price > MAX_PRICE:
        return False

    if source == "Realtor.ca":
        # Sqft con umbral mas flexible: excluir solo si es menor a 700
        if sqft is not None and sqft < 700:
            return False
    else:
        # Kijiji y Craigslist: sqft obligatorio
        if sqft is None:
            return False
        if sqft < MIN_SQFT:
            return False

    return True


def load_seen():
    """Carga la lista de anuncios ya vistos."""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(seen):
    """Guarda la lista de anuncios ya vistos."""
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def main():
    print(f"\n{'='*50}")
    print(f"  Buscador de arriendos — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")

    # 1. Recolectar anuncios de todos los sitios
    all_listings = []
    all_listings += kijiji.scrape()
    all_listings += craigslist.scrape()
    all_listings += realtorca.scrape()

    # Calcular distancias al colegio y al subway
    print("\n Calculando distancias...")
    for i, listing in enumerate(all_listings):
        all_listings[i] = enrich_listing(listing)
    print(f" Distancias calculadas para {len(all_listings)} propiedades")

    print(f"\n Total recolectados antes de filtrar: {len(all_listings)} anuncios")

    # Aplicar filtros de precio y sqft
    all_listings = [l for l in all_listings if meets_filters(l)]
    print(f" Despues de filtros (precio <= ${MAX_PRICE}, sqft >= {MIN_SQFT}): {len(all_listings)} anuncios")

    # 2. Cargar anuncios ya vistos
    seen = load_seen()

    # IDs activos en este scrape
    current_ids = {listing["id"] for listing in all_listings}

    # 3. Detectar cuales son nuevos
    #    Solo son "nuevos" si no estaban en seen O si habian expirado antes
    new_listings = []
    for listing in all_listings:
        entry = seen.get(listing["id"])
        if entry is None or entry.get("expired"):
            # Es nuevo (o reaparecio despues de expirar)
            new_listings.append(listing)
            seen[listing["id"]] = {
                "first_seen": entry["first_seen"] if entry else datetime.utcnow().isoformat(),
                "title": listing["title"],
                "active": True,
            }
        else:
            # Ya conocido y sigue activo
            seen[listing["id"]]["active"] = True
            seen[listing["id"]].pop("expired", None)

    print(f" Nuevos anuncios: {len(new_listings)}")

    # 4. Detectar cuales expiraron (estaban activos, ya no aparecen)
    expired_count = 0
    for uid, entry in seen.items():
        if uid not in current_ids and not entry.get("expired"):
            entry["expired"] = True
            entry["active"] = False
            expired_count += 1

    if expired_count:
        print(f" Anuncios expirados (ya no disponibles): {expired_count}")

    # 5. Enviar notificacion si hay nuevos
    if new_listings:
        send_notification(new_listings)

    # 6. Guardar los anuncios vistos (para no repetir notificaciones)
    save_seen(seen)

    # 7. Generar la pagina web con TODOS los anuncios del scrape actual
    generate(all_listings)

    print(f"\n Listo! {len(all_listings)} propiedades en la pagina web.\n")


if __name__ == "__main__":
    main()
