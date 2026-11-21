"""Carga del archivo crudo y verificación de su esquema.

Este archivo no guarda rutas ni listas de columnas: el notebook se las
entrega a cargar() como argumentos. Así la configuración vive en un solo lugar.
"""
import os
from pathlib import Path

import pandas as pd


def leer_archivo(ruta):
    """Lee el archivo según su extensión y devuelve un DataFrame."""
    extension = os.path.splitext(ruta)[1].lower()

    if extension in (".csv", ".txt"):
        # sep=None con engine="python" infiere el separador (coma o punto y coma)
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


def cargar(ruta, columnas_esperadas):
    """Carga el archivo crudo y verifica que estén las columnas del pipeline."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}\n"
            "Descárguenlo según el README y guárdenlo como data/raw/datasetairbnb.csv."
        )
    df = leer_archivo(ruta)
    print(f"Archivo leído: {ruta}")

    informe = verificar_esquema(df, columnas_esperadas)
    print(f"Forma: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Esquema verificado: las {informe['declaradas']} columnas del pipeline están presentes")
    return df


# Esto solo se ejecuta si corren "python src/carga.py" desde la raíz del proyecto.
# Al IMPORTAR el módulo desde el notebook, este bloque NO se ejecuta.
if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]          # la carpeta superior a src/
    datos = cargar(str(raiz / "data" / "raw" / "datasetairbnb.csv"), ["id", "price"])
    print(datos[["id", "price"]].head())