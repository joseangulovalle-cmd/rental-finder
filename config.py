# ============================================================
#  CONFIGURACION DEL PROYECTO - Buscador de Arriendos Toronto
# ============================================================

# Coordenadas del colegio (250 Madison Ave, Toronto)
SCHOOL_LAT  = 43.6802
SCHOOL_LON  = -79.3959
SCHOOL_NAME = "Waldorf Academy (250 Madison Ave)"

# Radio de busqueda: ~1.2 km = aprox 15 min caminando (margen amplio)
MAX_DISTANCE_KM = 1.2

# Filtros de propiedad
MIN_BEDROOMS = 2
MIN_BATHROOMS = 2
PROPERTY_TYPE = "rental"  # Solo arriendos

# Emails para notificaciones
NOTIFY_EMAILS = [
    "jose.angulo.valle@gmail.com",
    "kiyomi.olivares@gmail.com",
]

# Archivo donde guardamos los anuncios ya vistos (para no repetir notificaciones)
SEEN_FILE = "data/seen.json"

# Archivo HTML generado (la pagina web)
OUTPUT_HTML = "index.html"
