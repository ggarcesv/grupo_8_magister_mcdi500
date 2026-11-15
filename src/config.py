"""Configuración única del estudio (Fases 2, 3 y 4).

Este módulo NO procesa datos: declara las decisiones que la Fase 2 justificó
con cifras, para que ningún cuaderno posterior las vuelva a escribir a mano.
Si una decisión cambia, cambia aquí y se propaga a todas las fases.
"""

from pathlib import Path

# --------------------------------------------------------------------------
# Rutas (relativas a la raíz del repositorio)
# --------------------------------------------------------------------------
SEMILLA = 42
ARCHIVO_CRUDO = Path("data") / "raw" / "datasetairbnb.csv"
ARCHIVO_PROCESADO_F2 = Path("data") / "processed" / "airbnb_procesado.csv"
ARCHIVO_DICCIONARIO = Path("docs") / "diccionario_variables.csv"
DIR_PROCESADO = Path("data") / "processed"
DIR_DOCS = Path("docs")

# --------------------------------------------------------------------------
# Delimitación del estudio (decisión F2, sección 3a)
# --------------------------------------------------------------------------
COLUMNA_ID = "id"
COLUMNA_FILTRO = "room_type"
VALOR_FILTRO = "Entire home/apt"          # la pregunta estudia alojamientos completos

# --------------------------------------------------------------------------
# Roles de las variables en el estudio (decisión F2, sección 2)
# --------------------------------------------------------------------------
OBJETIVOS = ["price", "estimated_occupancy_l365d"]
EXPLICATIVAS = {
    "comodidades": ["amenities"],
    "capacidad":   ["accommodates", "bedrooms", "beds"],
    "ubicacion":   ["neighbourhood_cleansed", "latitude"],
    "control":     ["host_is_superhost", "minimum_nights", "maximum_nights"],
}
VARIABLES_ESTUDIO = OBJETIVOS + [v for grupo in EXPLICATIVAS.values() for v in grupo]

# Columnas que el archivo crudo DEBE traer para que el pipeline tenga sentido
COLUMNAS_REQUERIDAS = [COLUMNA_ID, COLUMNA_FILTRO] + VARIABLES_ESTUDIO

# --------------------------------------------------------------------------
# Limpieza (decisiones F2, sección 3b-3e)
# --------------------------------------------------------------------------
TOPE_MAXIMUM_NIGHTS = 1125          # máximo real de la plataforma; sobre eso es basura del sistema
UMBRAL_PRECIO = 10_000_000          # sobre este valor no hay precios intermedios: digitación
COLUMNAS_IMPUTAR = ["accommodates", "latitude", "bedrooms", "beds",
                    "minimum_nights", "maximum_nights"]
COLUMNA_CON_BANDERA = "bedrooms"    # se conserva la marca de qué filas se imputaron

# --------------------------------------------------------------------------
# Transformación (decisiones F2, sección 4)
# --------------------------------------------------------------------------
COMODIDADES = {
    "tiene_aire_acondicionado": r"air conditioning|\bac\b",
    "tiene_estacionamiento":    r"parking",
    "tiene_piscina":            r"\bpool\b(?! table)",
    "tiene_lavadora":           r"\bwasher\b",
    "tiene_gimnasio":           r"\bgym\b",
    "tiene_ascensor":           r"elevator",
    "tiene_espacio_trabajo":    r"dedicated workspace",
    "tiene_self_checkin":       r"self check-in",
}
# columna nominal -> prefijo de las columnas one-hot (nombres idénticos a F2)
NOMINALES = {"host_is_superhost": "superhost", "neighbourhood_cleansed": "comuna"}

# --------------------------------------------------------------------------
# Escalamiento (decisión F2, sección 5): RobustScaler sobre las explicativas numéricas
# --------------------------------------------------------------------------
COLUMNAS_ESCALAR = ["accommodates", "latitude", "bedrooms", "beds",
                    "minimum_nights", "maximum_nights", "n_comodidades"]

# --------------------------------------------------------------------------
# Partición (nuevo en F3): el ajuste se hace solo con entrenamiento
# --------------------------------------------------------------------------
PROPORCION_PRUEBA = 0.2


def localizar_raiz(inicio=None):
    """Devuelve la raíz del proyecto aunque el kernel se abra en F1/F2/F3/F4."""
    inicio = Path.cwd() if inicio is None else Path(inicio)
    return inicio.parent if inicio.name in {"F1", "F2", "F3", "F4"} else inicio
