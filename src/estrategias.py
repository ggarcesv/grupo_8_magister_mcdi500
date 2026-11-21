"""Estrategias de imputación (patrón Strategy).

Cada estrategia sabe CÓMO calcular el valor de relleno de una columna.
ImputadorFlexible (en transformadores.py) decide CUÁNDO aprenderlo y aplicarlo.
Agregar una estrategia nueva no obliga a modificar el imputador ni el pipeline.
"""


class EstrategiaImputacion:
    """Contrato común: toda estrategia implementa calcular(df, columna)."""

    etiqueta = "sin definir"

    def calcular(self, df, columna):
        raise NotImplementedError("Cada estrategia debe implementar calcular().")


class PorMediana(EstrategiaImputacion):
    """Mediana de la columna: la elegida por el proyecto (variables asimétricas)."""

    etiqueta = "mediana"

    def calcular(self, df, columna):
        return float(df[columna].median())


class PorMedia(EstrategiaImputacion):
    """Media de la columna: alternativa comparada en la Fase 2."""

    etiqueta = "media"

    def calcular(self, df, columna):
        return float(df[columna].mean())


class PorMedianaDeGrupo(EstrategiaImputacion):
    """Mediana de la columna dentro de cada grupo (por ejemplo, por comuna)."""

    etiqueta = "mediana por grupo"

    def __init__(self, columna_grupo):
        self.columna_grupo = columna_grupo

    def calcular(self, df, columna):
        return df.groupby(self.columna_grupo)[columna].median().to_dict()