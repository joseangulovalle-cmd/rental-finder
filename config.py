# ============================================================
#  CONFIGURACION DEL PROYECTO - Buscador de Arriendos Toronto
# ============================================================

# Coordenadas del colegio (250 Madison Ave, Toronto)
SCHOOL_LAT  = 43.6772
SCHOOL_LON  = -79.4071
SCHOOL_NAME = "Waldorf Academy (250 Madison Ave)"

# Radio de busqueda: ~1.2 km = aprox 15 min caminando (margen amplio)
MAX_DISTANCE_KM = 1.2

# Filtros de propiedad
MIN_BEDROOMS = 2
MIN_BATHROOMS = 2
PROPERTY_TYPE = "rental"  # Solo arriendos
MAX_PRICE = 4000           # Precio maximo mensual en CAD
MIN_SQFT = 800             # Superficie minima en pies cuadrados

# Emails para notificaciones (se leen de secrets, no estan escritos aqui)
import os
NOTIFY_EMAILS = [
    e.strip()
    for e in os.environ.get("NOTIFY_EMAILS", "").split(",")
    if e.strip()
]

# Archivo donde guardamos los anuncios ya vistos (para no repetir notificaciones)
SEEN_FILE = "data/seen.json"

# Archivo HTML generado (la pagina web)
OUTPUT_HTML = "index.html"

# JSONbin.io — para guardar favoritos/descartados compartidos entre usuarios
# 1. Crear cuenta gratis en jsonbin.io
# 2. Crear un bin con: {"favorites": [], "hidden": []}
# 3. Pegar el Bin ID y Master Key abajo
JSONBIN_BIN_ID  = os.environ.get("JSONBIN_BIN_ID", "")
JSONBIN_API_KEY = os.environ.get("JSONBIN_API_KEY", "")
