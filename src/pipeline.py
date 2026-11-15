"""Pipeline: encadena transformadores y controla el orden ajustar -> transformar.

El pipeline no sabe qué hace cada paso (bajo acoplamiento): solo exige que sea
un `Transformador`. Agregar un paso nuevo no obliga a tocar esta clase.
"""

import time

import pandas as pd

from .transformadores import ErrorDePipeline, Transformador


class Pipeline:
    """Secuencia ordenada de transformadores con un único punto de ajuste."""

    def __init__(self, pasos=None):
        self._pasos = []
        self._ajustado = False
        for paso in pasos or []:
            self.agregar(paso)

    # ---- composición ---------------------------------------------------------
    def agregar(self, transformador):
        if not isinstance(transformador, Transformador):
            raise TypeError(
                f"Pipeline: se esperaba un Transformador y se recibió {type(transformador).__name__}."
            )
        self._pasos.append(transformador)
        self._ajustado = False
        return self

    # ---- contrato (el mismo que un Transformador: un pipeline se puede anidar) ----
    def ajustar(self, df):
        """Ajusta cada paso con la salida del anterior, SOLO con estos datos."""
        intermedio = df.copy()
        for paso in self._pasos:
            intermedio = self._ejecutar(paso, intermedio, ajustar=True)
        self._ajustado = True
        return self

    def transformar(self, df):
        if not self._ajustado:
            raise ErrorDePipeline("Pipeline: hay que ajustar antes de transformar.")
        resultado = df.copy()
        for paso in self._pasos:
            resultado = self._ejecutar(paso, resultado, ajustar=False)
        return resultado

    def ajustar_transformar(self, df):
        return self.ajustar(df).transformar(df)

    def _ejecutar(self, paso, df, ajustar):
        """Punto único de ejecución: las subclases lo extienden (por ejemplo, para observar)."""
        return paso.ajustar_transformar(df) if ajustar else paso.transformar(df)

    # ---- introspección -------------------------------------------------------
    @property
    def ajustado(self):
        return self._ajustado

    @property
    def pasos(self):
        return tuple(self._pasos)             # copia inmutable: no se altera desde fuera

    def parametros(self):
        """Diccionario anidado {paso: parámetros}. Es la entrada de aplanar() (recursión)."""
        return {f"{i:02d}.{p.nombre}": p.parametros for i, p in enumerate(self._pasos, start=1)}

    def resumen(self):
        return pd.DataFrame([
            {"orden": i, "paso": p.nombre, "clase": type(p).__name__, "ajustado": p.ajustado}
            for i, p in enumerate(self._pasos, start=1)
        ])

    def __len__(self):
        return len(self._pasos)

    def __iter__(self):
        return iter(self._pasos)

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"Pipeline({len(self._pasos)} pasos, {estado})"


class PipelineObservable(Pipeline):
    """Pipeline que avisa a sus observadores al terminar cada paso (patrón Observer).

    El pipeline no sabe quién escucha ni qué hace con el aviso: la bitácora,
    la consola o un archivo se suscriben desde fuera.
    """

    def __init__(self, pasos=None):
        super().__init__(pasos)
        self._observadores = []

    def suscribir(self, observador):
        if not callable(getattr(observador, "notificar", None)):
            raise TypeError("Un observador debe implementar notificar(evento).")
        self._observadores.append(observador)
        return self

    def _ejecutar(self, paso, df, ajustar):
        filas_antes, columnas_antes = df.shape
        inicio = time.perf_counter()
        resultado = super()._ejecutar(paso, df, ajustar)
        evento = {
            "fase": "ajuste" if ajustar else "transformacion",
            "paso": paso.nombre,
            "filas_antes": filas_antes, "filas_despues": resultado.shape[0],
            "columnas_antes": columnas_antes, "columnas_despues": resultado.shape[1],
            "segundos": time.perf_counter() - inicio,
            "parametros": paso.parametros,
        }
        for observador in self._observadores:
            observador.notificar(evento)
        return resultado
