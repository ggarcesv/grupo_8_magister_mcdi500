def leer_archivo(ruta):
    """Lee el archivo según su extensión y devuelve un DataFrame."""
    extension = os.path.splitext(ruta)[1].lower()

    if extension in (".csv", ".txt"):
        # sep=None con engine="python" infiere el separador: útil con datos
        # públicos chilenos, que suelen venir con punto y coma
        return pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8")
    if extension in (".xlsx", ".xls"):
        return pd.read_excel(ruta)
    if extension == ".parquet":
        return pd.read_parquet(ruta)

    raise ValueError(
        f"Extensión no reconocida: '{extension}'. "
        "Se admiten .csv, .txt, .xlsx, .xls y .parquet."
    )


def verificar_esquema(df, columnas_esperadas):
    """Comprueba que estén todas las columnas declaradas en la configuración."""
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        raise KeyError(
            f"Faltan columnas declaradas en la configuración: {faltantes}\n"
            f"Columnas disponibles en el archivo: {list(df.columns)}"
        )
    sobrantes = [c for c in df.columns if c not in columnas_esperadas]
    return {"declaradas": len(columnas_esperadas),
            "en_archivo": df.shape[1],
            "no_declaradas": sobrantes}
def cargar(ruta=RUTA_DATOS, columnas_esperadas=None):
    """Carga el archivo crudo y verifica que estén las columnas del pipeline."""
    columnas_esperadas = columnas_esperadas or COLUMNAS_ESPERADAS

    # Si el archivo no está, se detiene con un mensaje que dice qué hacer
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}\n"
            "Descárguenlo según el README y guárdenlo como data/raw/datasetairbnb.csv."
        )
    df = leer_archivo(ruta)
    print(f"Archivo leído: {ruta}")

    # Revisa que estén las 13 columnas que usa el pipeline
    informe = verificar_esquema(df, columnas_esperadas)
    print(f"Forma: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Esquema verificado: las {informe['declaradas']} columnas del pipeline están presentes")
    return df


datos = cargar()
datos.head()