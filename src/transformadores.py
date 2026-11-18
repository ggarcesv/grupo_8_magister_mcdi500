"""Pasos del pipeline de preprocesamiento (Fase 2 encapsulada en clases).

Todas las clases heredan de Transformador, que define el contrato común:
    ajustar(df)     -> aprende lo necesario del conjunto (solo entrenamiento)
    transformar(df) -> aplica lo aprendido, sin volver a calcular nada

Este archivo solo DEFINE clases: no ejecuta nada al importarlo.
"""
import json

import pandas as pd

from src.utilidades import ProyectoError

# =====================================================================
# Clase base
# =====================================================================

class Transformador:
    """Clase base: lo que todos los pasos del pipeline de Airbnb comparten.

    Esta clase NO se usa directamente. Su trabajo es definir el contrato:
    qué métodos tendrá todo paso del pipeline y cómo se controla su estado.
    Las clases hijas solo completan lo que cambia de un paso a otro.
    """

    def __init__(self, columna):
        # Atributo público: el nombre de una columna o una lista de columnas
        self.columna = columna

        # Atributos con guion bajo: por convención, INTERNOS
        self._parametros = {}       # lo que el paso aprende del conjunto
        self._ajustado = False      # controla que no se transforme antes de ajustar

    def _columnas(self):
        """Devuelve siempre una lista, aunque se haya indicado una sola columna."""
        return [self.columna] if isinstance(self.columna, str) else list(self.columna)

    # @property convierte un método en algo que se lee como atributo:
    # se escribe paso.nombre y no paso.nombre(). Y como no hay setter,
    # el valor NO se puede asignar desde fuera. Eso es encapsulamiento.
    @property
    def nombre(self):
        etiqueta = self.columna if isinstance(self.columna, str) else ", ".join(self.columna)
        return f"{type(self).__name__}({etiqueta})"

    @property
    def parametros(self):
        # dict(...) entrega una COPIA (copia defensiva): quien la reciba no
        # puede modificar el estado interno del objeto
        return dict(self._parametros)

    def ajustar(self, df):
        """Aprende los parámetros del conjunto que recibe."""
        faltantes = [c for c in self._columnas() if c not in df.columns]
        if faltantes:
            raise KeyError(f"{self.nombre}: no existen las columnas {faltantes}.")
        self._parametros = self.aprender(df)
        self._ajustado = True
        return self                 # permite encadenar: paso.ajustar(df).transformar(df)

    def transformar(self, df):
        """Aplica la transformación usando lo aprendido en ajustar()."""
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: hay que ajustar antes de transformar.")
        return self.aplicar(df.copy())   # copy(): no modifica el DataFrame original

    def ajustar_transformar(self, df):
        """Atajo: aprender y aplicar sobre el mismo conjunto."""
        return self.ajustar(df).transformar(df)

    # ---- Métodos que cada clase hija DEBE implementar ----
    def aprender(self, df):
        raise NotImplementedError("Cada clase hija debe implementar aprender().")

    def aplicar(self, df):
        raise NotImplementedError("Cada clase hija debe implementar aplicar().")


# =====================================================================
# Pasos que APRENDEN algo de los datos
# =====================================================================

class ImputadorMediana(Transformador):
    """Rellena los nulos con la mediana aprendida en el ajuste."""

    def aprender(self, df):
        return {"mediana": float(df[self.columna].median()),
                "nulos_en_ajuste": int(df[self.columna].isna().sum())}

    def aplicar(self, df):
        df[self.columna] = df[self.columna].fillna(self._parametros["mediana"])
        return df


class CodificadorNominal(Transformador):
    """Convierte una columna de categorías en columnas 0/1 (One-Hot).

    El vocabulario se aprende en el ajuste: una categoría que solo aparece en
    prueba no genera columna nueva, porque el modelo no pudo aprender de ella.
    """

    def __init__(self, columna, prefijo=None):
        super().__init__(columna)
        # El prefijo da nombre a las columnas nuevas: "comuna" -> comuna_Providencia
        self.prefijo = prefijo or columna

    def aprender(self, df):
        # Ordenadas, para que el resultado sea el mismo en cada ejecución
        return {"categorias": sorted(df[self.columna].dropna().unique())}

    def aplicar(self, df):
        for categoria in self._parametros["categorias"]:
            etiqueta = str(categoria).strip().replace(" ", "_").replace("-", "_")
            df[f"{self.prefijo}_{etiqueta}"] = (df[self.columna] == categoria).astype(int)
        return df.drop(columns=[self.columna])


class EscaladorRobusto(Transformador):
    """Centra en la mediana y divide por el rango intercuartílico (RobustScaler).

    Es el escalador que eligió la Fase 2: la mediana y el RIC casi no cambian
    por unos pocos valores extremos, así que esos extremos no deciden la escala.
    """

    def aprender(self, df):
        q1, mediana, q3 = df[self.columna].quantile([0.25, 0.5, 0.75])
        ric = float(q3 - q1)
        # Si el RIC es 0 (columna casi constante) se divide por 1: evita dividir por cero
        return {"mediana": float(mediana), "ric": ric if ric != 0 else 1.0}

    def aplicar(self, df):
        # Vectorizado: la sección 10 del notebook mide por qué se eligió esta forma
        df[self.columna] = ((df[self.columna] - self._parametros["mediana"])
                            / self._parametros["ric"])
        return df


# =====================================================================
# Pasos de limpieza: reglas fijas, no aprenden nada de los datos.
# Igual heredan de Transformador para compartir la misma interfaz
# y que el Pipeline los recorra sin preguntar su tipo (polimorfismo).
# =====================================================================

class EliminadorColumnas(Transformador):
    """Quita columnas que no aportan al análisis, como el identificador."""

    def aprender(self, df):
        return {"existe": self.columna in df.columns}

    def aplicar(self, df):
        return df.drop(columns=[self.columna]) if self.columna in df.columns else df


class ConversorPrecio(Transformador):
    """Convierte el precio de texto ("$55,106.00") a número."""

    def aprender(self, df):
        return {"regla": "quitar '$' y ',' y convertir a número"}

    def aplicar(self, df):
        texto = (df[self.columna].astype(str)
                 .str.replace("$", "", regex=False)
                 .str.replace(",", "", regex=False)
                 .str.strip())
        df[self.columna] = pd.to_numeric(texto, errors="coerce")
        return df


class FiltroFilas(Transformador):
    """Conserva solo las filas que cumplen una condición.

    La condición es una función que recibe el DataFrame y devuelve True/False
    por fila. Así una misma clase sirve para los cuatro filtros de la Fase 2.
    """

    def __init__(self, columna, condicion, descripcion):
        super().__init__(columna)
        self.condicion = condicion
        self.descripcion = descripcion

    @property
    def nombre(self):
        # Sobrescritura: el nombre muestra la regla, que dice más que la columna
        return f"FiltroFilas({self.descripcion})"

    def aprender(self, df):
        return {"regla": self.descripcion}

    def aplicar(self, df):
        return df[self.condicion(df)].copy()


class SelectorColumnas(Transformador):
    """Conserva solo las variables del estudio, en el orden declarado."""

    @property
    def nombre(self):
        return f"SelectorColumnas({len(self._columnas())} variables)"

    def aprender(self, df):
        return {"conservadas": len(self._columnas())}

    def aplicar(self, df):
        return df[self._columnas()].copy()


class Acotador(Transformador):
    """Acota una columna a un máximo (maximum_nights trae valores imposibles)."""

    def __init__(self, columna, maximo):
        super().__init__(columna)
        self.maximo = maximo

    def aprender(self, df):
        return {"maximo": self.maximo,
                "valores_sobre_el_maximo": int((df[self.columna] > self.maximo).sum())}

    def aplicar(self, df):
        df[self.columna] = df[self.columna].clip(upper=self.maximo)
        return df


class MarcadorNulos(Transformador):
    """Bandera 0/1 de qué filas tenían el dato faltante. Va ANTES de imputar."""

    def aprender(self, df):
        return {"nulos_en_ajuste": int(df[self.columna].isna().sum())}

    def aplicar(self, df):
        df[f"{self.columna}_imputado"] = df[self.columna].isna().astype(int)
        return df


class ExtractorComodidades(Transformador):
    """Pasa la lista de texto 'amenities' a un conteo y a indicadores 0/1."""

    def __init__(self, columna, patrones):
        super().__init__(columna)
        self.patrones = dict(patrones)     # copia: no depende del diccionario externo

    def aprender(self, df):
        return {"indicadores": list(self.patrones)}

    def _leer_lista(self, texto, indice):
        """Convierte el texto JSON de una fila en lista; si falla, dice qué fila."""
        try:
            return json.loads(texto)
        except (json.JSONDecodeError, TypeError) as error:
            raise ProyectoError(
                f"{self.nombre}: la fila con índice {indice} tiene '{self.columna}' "
                f"mal formado: {str(texto)[:60]!r}"
            ) from error

    def aplicar(self, df):
        # Texto -> lista real, fila por fila; si una fila está mal formada, se informa cuál
        listas = pd.Series([self._leer_lista(t, i) for i, t in df[self.columna].items()],
                           index=df.index)
        texto = listas.apply(lambda lista: "|".join(lista).lower())
        df["n_comodidades"] = listas.str.len()
        for nueva, patron in self.patrones.items():
            df[nueva] = texto.str.contains(patron, regex=True).astype(int)
        return df.drop(columns=[self.columna])