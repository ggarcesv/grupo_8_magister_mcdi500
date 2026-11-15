"""Transcripción literal del pipeline de la Fase 2 (celdas sueltas) como una función.

Sirve como ORÁCULO: si el pipeline de clases produce exactamente esta salida,
la reorganización en objetos no alteró el resultado. Cuando existe
data/processed/airbnb_procesado.csv (la salida real de F2) se compara también
contra ese archivo.
"""
import json

import pandas as pd
from sklearn import preprocessing
from sklearn.preprocessing import RobustScaler


def referencia_f2(df_crudo, cfg):
    df_crudo = df_crudo.copy()
    # F2 §2: price viene como texto
    df_crudo["price"] = pd.to_numeric(
        df_crudo["price"].astype(str).str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False).str.strip(), errors="coerce")
    df = df_crudo.copy()
    # F2 §3a
    df = df[df[cfg.COLUMNA_FILTRO] == cfg.VALOR_FILTRO].copy()
    df = df[cfg.VARIABLES_ESTUDIO].copy()
    # F2 §3b
    df["maximum_nights"] = df["maximum_nights"].clip(upper=cfg.TOPE_MAXIMUM_NIGHTS)
    # F2 §3c
    df = df.dropna(subset=cfg.OBJETIVOS).copy()
    # F2 §3e
    for col in cfg.COLUMNAS_IMPUTAR:
        df[col] = df[col].fillna(df[col].median())
    # F2 §3d
    df = df[~(df["price"] > cfg.UMBRAL_PRECIO)].copy()
    df = df[~(df["bedrooms"] > df["accommodates"])].copy()
    df["bedrooms_imputado"] = df_crudo.loc[df.index, "bedrooms"].isna().astype(int)
    # F2 §4.1
    listas = df["amenities"].apply(json.loads)
    texto = listas.apply(lambda lista: "|".join(lista).lower())
    df["n_comodidades"] = listas.str.len()
    for columna, patron in cfg.COMODIDADES.items():
        df[columna] = texto.str.contains(patron, regex=True).astype(int)
    df = df.drop(columns=["amenities"])

    # F2 §4.2 (LabelEncoder + OneHotEncoder, nombres en orden alfabético)
    def codificar_one_hot(df, columna, nombres):
        le = preprocessing.LabelEncoder().fit(df[columna])
        codigos = le.transform(df[columna])
        ohe = preprocessing.OneHotEncoder().fit(codigos.reshape(-1, 1))
        matriz = ohe.transform(codigos.reshape(-1, 1)).toarray()
        nuevas = pd.DataFrame(matriz, columns=nombres, index=df.index).astype(int)
        df = df.drop(columns=[columna]).reset_index(drop=True)
        return pd.concat([df, nuevas.reset_index(drop=True)], axis=1)

    df = codificar_one_hot(df, "host_is_superhost",
                           [f"superhost_{c}" for c in sorted(df["host_is_superhost"].unique())])
    df = codificar_one_hot(df, "neighbourhood_cleansed",
                           [f"comuna_{c.replace(' ', '_')}" for c in sorted(df["neighbourhood_cleansed"].unique())])
    # F2 §5
    df[cfg.COLUMNAS_ESCALAR] = RobustScaler().fit_transform(df[cfg.COLUMNAS_ESCALAR])
    return df
