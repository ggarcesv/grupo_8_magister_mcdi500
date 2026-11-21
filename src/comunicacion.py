from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd


def cargar_artefactos(carpeta: str | Path) -> dict[str, pd.DataFrame]:
    """Carga los cuatro artefactos tabulares generados en Fase 3 desde la carpeta indicada."""
    ruta = Path(carpeta)
    if not ruta.exists() or not ruta.is_dir():
        raise FileNotFoundError(f"No se encontró la carpeta de artefactos: {ruta}")

    archivos = {
        "entrenamiento": ruta / "entrenamiento_f3.csv",
        "prueba": ruta / "prueba_f3.csv",
        "parametros": ruta / "parametros_f3.csv",
        "diccionario": ruta / "diccionario_f3.csv",
    }

    artefactos: dict[str, pd.DataFrame] = {}
    for nombre, archivo in archivos.items():
        if not archivo.exists():
            raise FileNotFoundError(f"Falta el artefacto requerido: {archivo}")
        artefactos[nombre] = pd.read_csv(archivo)

    return artefactos


def leer_parametros(tabla: pd.DataFrame) -> dict[str, dict]:
    """Convierte la tabla de parámetros aprendidos (en formato JSON o clave=valor) en un diccionario."""
    if not isinstance(tabla, pd.DataFrame) or not {"paso", "parametros"}.issubset(tabla.columns):
        raise ValueError("La tabla de parámetros debe contener las columnas 'paso' y 'parametros'.")

    resultado: dict[str, dict] = {}
    for _, fila in tabla.iterrows():
        paso = str(fila["paso"]).strip()
        texto = str(fila["parametros"]).strip()

        if not texto:
            raise ValueError(f"Parámetros vacíos en el paso '{paso}'.")

        try:
            datos = json.loads(texto)
            if not isinstance(datos, dict):
                raise ValueError(f"El JSON de parámetros en '{paso}' no es un objeto.")
            resultado[paso] = datos
            continue
        except json.JSONDecodeError:
            if "=" not in texto:
                raise ValueError(f"Parámetros ilegibles en el paso '{paso}': '{texto}'")

            pares: dict[str, float] = {}
            for item in texto.split(";"):
                item = item.strip()
                if not item:
                    continue
                if "=" not in item:
                    raise ValueError(f"Par clave=valor mal formado en '{paso}': '{item}'")
                clave, valor_str = item.split("=", 1)
                try:
                    pares[clave.strip()] = float(valor_str.strip())
                except ValueError as exc:
                    raise ValueError(f"Valor no numérico en '{paso}': '{item}'") from exc

            if paso.startswith("EscaladorEstandar(") and not {"media", "desviacion"}.issubset(pares.keys()):
                raise ValueError(
                    f"Parámetros incompletos para '{paso}': se requieren 'media' y 'desviacion'."
                )

            resultado[paso] = pares

    return resultado


def revertir_escalamiento(
    df: pd.DataFrame, parametros: dict[str, dict]
) -> pd.DataFrame:
    """Revierte de forma vectorizada las columnas transformadas con EscaladorEstandar o EscaladorRobusto."""
    resultado = df.copy()
    for paso, valores in parametros.items():
        if paso.startswith("EscaladorEstandar(") and paso.endswith(")"):
            columna = paso[len("EscaladorEstandar(") : -1]
            if columna in resultado.columns:
                resultado[columna] = (
                    resultado[columna] * valores["desviacion"] + valores["media"]
                )
        elif paso.startswith("EscaladorRobusto(") and paso.endswith(")"):
            columna = paso[len("EscaladorRobusto(") : -1]
            if columna in resultado.columns:
                centro = valores.get("mediana", valores.get("centro", 0.0))
                escala = valores.get("ric", valores.get("iqr", valores.get("escala", 1.0)))
                resultado[columna] = resultado[columna] * escala + centro
    return resultado


def copia_interpretable(
    df: pd.DataFrame, parametros: dict[str, dict]
) -> pd.DataFrame:
    """Reconstruye una copia legible revirtiendo el escalamiento y recomponiendo variables nominales."""
    resultado = revertir_escalamiento(df, parametros)

    # Reconstruir host_is_superhost desde superhost_f / superhost_t con etiquetas originales ('t' / 'f')
    cols_superhost = [c for c in ["superhost_f", "superhost_t"] if c in resultado.columns]
    if cols_superhost:
        if "superhost_t" in resultado.columns:
            resultado["host_is_superhost"] = np.where(
                resultado["superhost_t"] == 1, "t", "f"
            )
        else:
            resultado["host_is_superhost"] = np.where(
                resultado["superhost_f"] == 1, "f", "t"
            )
        resultado = resultado.drop(columns=cols_superhost)

    # Reconstruir neighbourhood_cleansed desde comuna_<Nombre_Comuna>
    cols_comuna = [c for c in resultado.columns if c.startswith("comuna_")]
    if cols_comuna:
        matriz = resultado[cols_comuna].to_numpy()
        idx_max = matriz.argmax(axis=1)
        tiene_uno = matriz.max(axis=1) > 0
        nombres_comuna = [c[len("comuna_") :].replace("_", " ") for c in cols_comuna]
        resultado["neighbourhood_cleansed"] = np.where(
            tiene_uno,
            [nombres_comuna[i] for i in idx_max],
            "Otra",
        )
        resultado = resultado.drop(columns=cols_comuna)

    return resultado


def intervalo_wilson(
    casos: int | float, n: int | float, z: float = 1.96
) -> tuple[float, float]:
    """Calcula el intervalo de confianza de Wilson al 95 % para una proporción."""
    if n <= 0:
        raise ValueError("El total de observaciones 'n' debe ser mayor que cero.")
    if casos < 0 or casos > n:
        raise ValueError("El número de casos debe estar entre 0 y 'n'.")

    p = casos / n
    z2 = z**2
    denominador = 1.0 + z2 / n
    centro = (p + z2 / (2.0 * n)) / denominador
    margen = (z * np.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n)) / denominador

    inferior = 0.0 if casos == 0 else max(0.0, float(centro - margen))
    superior = 1.0 if casos == n else min(1.0, float(centro + margen))
    return inferior, superior


def tasa_por_grupo(
    df: pd.DataFrame, columna_grupo: str, columna_objetivo: str
) -> pd.DataFrame:
    """Calcula tamaño muestral, tasa de incidencia e IC 95 % de Wilson por grupo."""
    filas = []
    for grupo, sub in df.groupby(columna_grupo, observed=True):
        n = int(len(sub))
        casos = int(sub[columna_objetivo].sum())
        if n == 0:
            continue
        tasa = casos / n
        ic_inf, ic_sup = intervalo_wilson(casos, n)
        filas.append(
            {
                columna_grupo: grupo,
                "n": n,
                "casos": casos,
                "tasa": tasa,
                "ic_inferior": ic_inf,
                "ic_superior": ic_sup,
            }
        )

    return pd.DataFrame(filas)


def guardar_figura(
    figura: Any, carpeta: str | Path, nombre: str, dpi: int = 200
) -> Path:
    """Guarda una figura de matplotlib en formato PNG a 200 ppp y devuelve su ruta."""
    directorio = Path(carpeta)
    directorio.mkdir(parents=True, exist_ok=True)
    archivo = nombre if nombre.lower().endswith(".png") else f"{nombre}.png"
    destino = directorio / archivo
    figura.savefig(destino, dpi=dpi, bbox_inches="tight")
    return destino