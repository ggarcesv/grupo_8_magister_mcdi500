"""Observadores del pipeline (patrón Observer): registran sin estorbar."""

import pandas as pd


class Bitacora:
    """Acumula cada evento del pipeline y lo entrega como tabla.

    Reemplaza la bitácora escrita a mano de la Fase 2: se genera en cada
    ejecución, así que no puede quedar desactualizada.
    """

    def __init__(self):
        self._eventos = []

    def notificar(self, evento):
        self._eventos.append(dict(evento))

    def a_dataframe(self):
        if not self._eventos:
            return pd.DataFrame()
        tabla = pd.DataFrame(self._eventos)
        tabla["filas_eliminadas"] = tabla["filas_antes"] - tabla["filas_despues"]
        tabla["columnas_delta"] = tabla["columnas_despues"] - tabla["columnas_antes"]
        tabla["segundos"] = tabla["segundos"].round(5)
        tabla["parametros"] = tabla["parametros"].map(lambda p: _resumir(p))
        return tabla[["fase", "paso", "filas_antes", "filas_despues", "filas_eliminadas",
                      "columnas_despues", "columnas_delta", "segundos", "parametros"]]

    def guardar(self, ruta):
        self.a_dataframe().to_csv(ruta, index=False)
        return ruta

    def __len__(self):
        return len(self._eventos)


class ReporteConsola:
    """Imprime cada paso mientras ocurre."""

    def notificar(self, evento):
        print(f"  [{evento['fase'][:6]}] {evento['paso']:<46} "
              f"{evento['filas_antes']:>6} -> {evento['filas_despues']:>6} filas, "
              f"{evento['columnas_despues']:>3} col  [{evento['segundos']:.4f}s]")


def _resumir(parametros, maximo=90):
    """Representación corta de los parámetros para que la tabla sea legible."""
    texto = str(parametros)
    return texto if len(texto) <= maximo else texto[: maximo - 3] + "..."
