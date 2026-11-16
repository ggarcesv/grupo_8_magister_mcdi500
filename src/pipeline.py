"""Pipeline: encadena los transformadores y los ejecuta en orden.

Incluye construir_pipeline(config), que arma los pasos de la Fase 2 a partir
de la configuración que le entrega el notebook. Este archivo no conoce rutas
ni nombres de columna propios: todo llega por parámetro (bajo acoplamiento).
"""
import pandas as pd

from src.transformadores import (
    Acotador,
    CodificadorNominal,
    ConversorPrecio,
    EscaladorRobusto,
    ExtractorComodidades,
    FiltroFilas,
    ImputadorMediana,
    MarcadorNulos,
    SelectorColumnas,
    Transformador,
)


class Pipeline:
    """Encadena transformadores y los ejecuta en orden."""

    def __init__(self, pasos=None):
        self._pasos = []
        self._ajustado = False
        for paso in (pasos or []):
            self.agregar(paso)          # así también se valida cada paso inicial

    def agregar(self, transformador):
        if not isinstance(transformador, Transformador):
            raise TypeError(
                f"Se esperaba un Transformador y se recibió {type(transformador).__name__}."
            )
        self._pasos.append(transformador)
        return self

    def ajustar(self, df):
        """Aprende los parámetros de cada paso SOLO con estos datos."""
        intermedio = df.copy()
        for paso in self._pasos:
            intermedio = paso.ajustar_transformar(intermedio)
        self._ajustado = True
        return self

    def transformar(self, df):
        if not self._ajustado:
            raise RuntimeError("Pipeline: hay que ajustar antes de transformar.")
        resultado = df.copy()
        for paso in self._pasos:
            resultado = paso.transformar(resultado)
        return resultado

    def pasos_ejecutados(self):
        """Devuelve los pasos, para poder registrar sus parámetros aprendidos."""
        return tuple(self._pasos)

    def resumen(self):
        return pd.DataFrame([
            {"orden": i, "paso": p.nombre, "clase": type(p).__name__}
            for i, p in enumerate(self._pasos, start=1)
        ])

    def __len__(self):
        return len(self._pasos)

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"Pipeline({len(self._pasos)} pasos, {estado})"


def construir_pipeline(config):
    """Arma el pipeline de la Fase 2, en el MISMO orden, desde la configuración.

    config es un diccionario con estas claves (salen de la celda de
    configuración del notebook):
        objetivos, variables_estudio, columnas_imputar, columnas_marcar,
        columnas_nominales, columnas_escalar, comodidades,
        umbral_precio, max_noches
    """
    objetivos = config["objetivos"]
    umbral = config["umbral_precio"]

    pasos = [
        ConversorPrecio("price"),
        FiltroFilas("room_type", lambda d: d["room_type"] == "Entire home/apt",
                    "solo alojamientos completos"),
        SelectorColumnas(config["variables_estudio"]),
        Acotador("maximum_nights", config["max_noches"]),
        FiltroFilas(objetivos, lambda d: d[objetivos].notna().all(axis=1),
                    "objetivos sin faltantes"),
    ]
    pasos += [MarcadorNulos(c) for c in config["columnas_marcar"]]
    pasos += [ImputadorMediana(c) for c in config["columnas_imputar"]]
    pasos += [
        FiltroFilas("price", lambda d: ~(d["price"] > umbral), f"precio <= {umbral:,}"),
        FiltroFilas(["bedrooms", "accommodates"],
                    lambda d: ~(d["bedrooms"] > d["accommodates"]),
                    "dormitorios <= huéspedes"),
        ExtractorComodidades("amenities", config["comodidades"]),
    ]
    pasos += [CodificadorNominal(c, prefijo)
              for c, prefijo in config["columnas_nominales"].items()]
    pasos += [EscaladorRobusto(c) for c in config["columnas_escalar"]]
    return Pipeline(pasos)