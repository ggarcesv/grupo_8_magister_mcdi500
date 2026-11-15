"""Lectura y verificación del archivo de datos. Una sola responsabilidad: entrada."""

from pathlib import Path

import pandas as pd


class EsquemaInvalidoError(KeyError):
    """El archivo no trae las columnas que el estudio declara."""


def leer_archivo(ruta, na_values=("N/A",)):
    """Lee CSV/Parquet/Excel según la extensión. Lanza FileNotFoundError si no existe."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta.name} en {ruta.parent.resolve()}. "
            "Descárguelo con la celda de descarga del cuaderno F1 (data/raw/)."
        )
    extension = ruta.suffix.lower()
    if extension in (".csv", ".txt"):
        # na_values deja constancia de que los faltantes vienen como texto 'N/A' (igual que F2)
        return pd.read_csv(ruta, na_values=list(na_values))
    if extension == ".parquet":
        return pd.read_parquet(ruta)
    if extension in (".xlsx", ".xls"):
        return pd.read_excel(ruta)
    raise ValueError(f"Extensión no admitida: '{extension}'. Use .csv, .parquet o .xlsx.")


def verificar_esquema(df, columnas_requeridas):
    """Comprueba que estén las columnas requeridas; devuelve un informe dict."""
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise EsquemaInvalidoError(
            f"Faltan columnas requeridas por el estudio: {faltantes}. "
            f"El archivo trae {df.shape[1]} columnas."
        )
    return {
        "filas": int(df.shape[0]),
        "columnas_archivo": int(df.shape[1]),
        "columnas_requeridas": len(columnas_requeridas),
        "columnas_no_usadas": int(df.shape[1] - len(columnas_requeridas)),
    }


def cargar(ruta, columnas_requeridas):
    """Lee el archivo y verifica el esquema. Devuelve (DataFrame, informe)."""
    df = leer_archivo(ruta)
    informe = verificar_esquema(df, columnas_requeridas)
    return df, informe
