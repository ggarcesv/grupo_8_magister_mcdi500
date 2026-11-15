"""Transformadores del pipeline: la clase base y una clase hija por paso de la Fase 2.

Diseño
------
* `Transformador` define el CONTRATO (ajustar / transformar) y controla el estado:
  valida la entrada, impide transformar antes de ajustar y protege los parámetros
  aprendidos (encapsulamiento). No sabe QUÉ se aprende: eso lo delega a las hijas.
* Cada hija implementa solo `aprender(df) -> dict` y `aplicar(df) -> df`
  (herencia). El pipeline las recorre sin preguntar su tipo (polimorfismo).
* Las estrategias de imputación son objetos intercambiables (patrón Strategy):
  el `Imputador` sabe CUÁNDO imputar; la estrategia sabe CÓMO.

Cada paso corresponde a una decisión documentada en el cuaderno de la Fase 2;
el número de sección se indica en el docstring de cada clase.
"""

import json
import re

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler


class ErrorDePipeline(Exception):
    """Error propio del proyecto: permite distinguirlo de los de pandas o sklearn."""


# ============================================================================
# Clase base
# ============================================================================
class Transformador:
    """Clase base de todos los pasos. No se instancia directamente.

    Parámetros
    ----------
    columna : str | list[str] | None
        Columna(s) sobre las que opera el paso. None si el paso opera sobre
        toda la tabla (por ejemplo, la selección de columnas).
    """

    def __init__(self, columna=None):
        self.columna = columna
        self._parametros = {}      # interno: lo aprendido en ajustar()
        self._ajustado = False     # interno: controla el orden de las llamadas

    # ---- propiedades de solo lectura (encapsulamiento) ----------------------
    @property
    def nombre(self):
        if self.columna is None:
            return type(self).__name__
        if isinstance(self.columna, (list, tuple)):
            return f"{type(self).__name__}({len(self.columna)} columnas)"
        return f"{type(self).__name__}({self.columna})"

    @property
    def parametros(self):
        return dict(self._parametros)          # copia defensiva

    @property
    def ajustado(self):
        return self._ajustado

    # ---- validación común ----------------------------------------------------
    def _columnas_necesarias(self):
        if self.columna is None:
            return []
        return list(self.columna) if isinstance(self.columna, (list, tuple)) else [self.columna]

    def _validar(self, df):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{self.nombre}: se esperaba un DataFrame y se recibió {type(df).__name__}.")
        faltan = [c for c in self._columnas_necesarias() if c not in df.columns]
        if faltan:
            raise KeyError(f"{self.nombre}: faltan las columnas {faltan}.")

    # ---- contrato público ----------------------------------------------------
    def ajustar(self, df):
        """Aprende los parámetros SOLO del conjunto recibido (entrenamiento)."""
        self._validar(df)
        self._parametros = self.aprender(df)
        self._ajustado = True
        return self

    def transformar(self, df):
        """Aplica lo aprendido a cualquier conjunto. Exige ajustar() previo."""
        if not self._ajustado:
            raise ErrorDePipeline(f"{self.nombre}: hay que ajustar antes de transformar.")
        self._validar(df)
        return self.aplicar(df.copy())         # copia: no se altera el DataFrame del usuario

    def ajustar_transformar(self, df):
        return self.ajustar(df).transformar(df)

    # ---- lo que cada hija DEBE implementar -----------------------------------
    def aprender(self, df):
        raise NotImplementedError(f"{type(self).__name__} debe implementar aprender().")

    def aplicar(self, df):
        raise NotImplementedError(f"{type(self).__name__} debe implementar aplicar().")

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"<{self.nombre} · {estado}>"


# ============================================================================
# Pasos que delimitan el conjunto (F2, sección 3a)
# ============================================================================
class FiltroCategoria(Transformador):
    """Conserva las filas cuya columna vale `valor` (F2 §3a: solo alojamientos completos)."""

    def __init__(self, columna, valor):
        super().__init__(columna)
        self.valor = valor

    def aprender(self, df):
        mascara = df[self.columna] == self.valor
        return {"valor": self.valor, "conservadas_en_ajuste": int(mascara.sum()),
                "descartadas_en_ajuste": int((~mascara).sum())}

    def aplicar(self, df):
        return df[df[self.columna] == self.valor].copy()


class SelectorColumnas(Transformador):
    """Conserva solo las variables del estudio, en el orden declarado (F2 §3a)."""

    def __init__(self, columnas):
        super().__init__(list(columnas))

    def aprender(self, df):
        return {"conservadas": len(self.columna),
                "descartadas": int(df.shape[1] - len(self.columna))}

    def aplicar(self, df):
        return df[self.columna].copy()


# ============================================================================
# Limpieza (F2, sección 3b-3e)
# ============================================================================
class ConvertidorMoneda(Transformador):
    """Convierte texto monetario ('$55,106.00') a número (F2 §2). Lo no convertible queda NaN."""

    _patron = re.compile(r"[$,\s]")

    def _convertir(self, serie):
        limpio = serie.astype(str).str.replace(self._patron, "", regex=True)
        return pd.to_numeric(limpio, errors="coerce")

    def aprender(self, df):
        original = df[self.columna]
        convertido = self._convertir(original)
        return {"ya_numerica": bool(pd.api.types.is_numeric_dtype(original)),
                "no_convertibles": int(convertido.isna().sum() - original.isna().sum())}

    def aplicar(self, df):
        if not pd.api.types.is_numeric_dtype(df[self.columna]):
            df[self.columna] = self._convertir(df[self.columna])
        return df


class AcotadorSuperior(Transformador):
    """Acota los valores sobre `tope` (F2 §3b: maximum_nights a 1125, el máximo de la plataforma)."""

    def __init__(self, columna, tope):
        super().__init__(columna)
        self.tope = tope

    def aprender(self, df):
        return {"tope": self.tope, "acotados_en_ajuste": int((df[self.columna] > self.tope).sum())}

    def aplicar(self, df):
        df[self.columna] = df[self.columna].clip(upper=self.tope)
        return df


class EliminadorNulos(Transformador):
    """Elimina filas con nulos en las columnas dadas (F2 §3c: los objetivos no se imputan)."""

    def __init__(self, columnas):
        super().__init__(list(columnas))

    def aprender(self, df):
        return {"eliminadas_en_ajuste": int(df[self.columna].isna().any(axis=1).sum())}

    def aplicar(self, df):
        return df.dropna(subset=self.columna).copy()


class FiltroMaximo(Transformador):
    """Elimina filas con valor sobre `maximo` (F2 §3d: precios imposibles sobre $10.000.000)."""

    def __init__(self, columna, maximo):
        super().__init__(columna)
        self.maximo = maximo

    def aprender(self, df):
        return {"maximo": self.maximo, "eliminadas_en_ajuste": int((df[self.columna] > self.maximo).sum())}

    def aplicar(self, df):
        return df[~(df[self.columna] > self.maximo)].copy()


class FiltroCoherencia(Transformador):
    """Elimina filas donde columna_a > columna_b (F2 §3d: más dormitorios que huéspedes)."""

    def __init__(self, columna_a, columna_b):
        super().__init__([columna_a, columna_b])
        self.columna_a, self.columna_b = columna_a, columna_b

    @property
    def nombre(self):
        return f"FiltroCoherencia({self.columna_a} <= {self.columna_b})"

    def aprender(self, df):
        return {"eliminadas_en_ajuste": int((df[self.columna_a] > df[self.columna_b]).sum())}

    def aplicar(self, df):
        return df[~(df[self.columna_a] > df[self.columna_b])].copy()


# ============================================================================
# Imputación con estrategia intercambiable (patrón Strategy) — F2 §3e
# ============================================================================
class EstrategiaImputacion:
    """Contrato: calcular(df, columna) devuelve el valor (o dict por grupo) de relleno."""
    etiqueta = "sin definir"

    def calcular(self, df, columna):
        raise NotImplementedError


class PorMediana(EstrategiaImputacion):
    etiqueta = "mediana"

    def calcular(self, df, columna):
        return float(df[columna].median())


class PorMedia(EstrategiaImputacion):
    etiqueta = "media"

    def calcular(self, df, columna):
        return float(df[columna].mean())


class PorMedianaDeGrupo(EstrategiaImputacion):
    """Mediana dentro de cada grupo de `columna_grupo`; respaldo con la mediana global."""

    def __init__(self, columna_grupo):
        self.columna_grupo = columna_grupo
        self.etiqueta = f"mediana por {columna_grupo}"

    def calcular(self, df, columna):
        por_grupo = df.groupby(self.columna_grupo, observed=True)[columna].median().to_dict()
        return {"grupos": por_grupo, "global": float(df[columna].median())}


class Imputador(Transformador):
    """Rellena nulos con el valor que calcula la estrategia (por defecto, la mediana).

    bandera=True agrega la columna `<columna>_imputado` (1 = fue rellenado), como
    hizo la Fase 2 con `bedrooms`.
    """

    def __init__(self, columna, estrategia=None, bandera=False):
        super().__init__(columna)
        self.estrategia = estrategia or PorMediana()
        if not isinstance(self.estrategia, EstrategiaImputacion):
            raise TypeError("estrategia debe ser una EstrategiaImputacion.")
        self.bandera = bandera

    def aprender(self, df):
        return {"estrategia": self.estrategia.etiqueta,
                "valor": self.estrategia.calcular(df, self.columna),
                "nulos_en_ajuste": int(df[self.columna].isna().sum())}

    def aplicar(self, df):
        valor = self._parametros["valor"]
        if self.bandera:
            df[f"{self.columna}_imputado"] = df[self.columna].isna().astype(int)
        if isinstance(valor, dict):                             # mediana por grupo
            grupo = self.estrategia.columna_grupo
            relleno = df[grupo].map(valor["grupos"]).fillna(valor["global"])
            df[self.columna] = df[self.columna].fillna(relleno)
        else:
            df[self.columna] = df[self.columna].fillna(valor)
        return df


class ImputadorMediana(Imputador):
    """Atajo legible: Imputador con la estrategia de la mediana (la decisión de F2)."""

    def __init__(self, columna, bandera=False):
        super().__init__(columna, PorMediana(), bandera)


# ============================================================================
# Transformación (F2, sección 4)
# ============================================================================
class ExtractorComodidades(Transformador):
    """De la lista de texto `amenities` a `n_comodidades` + indicadores 0/1 (F2 §4.1).

    Implementación: bucle fila a fila en Python con patrones precompilados. La Fase 2
    usaba `Series.str.contains`; el benchmark de la Fase 3 (sección 8) mostró tiempo
    equivalente y ~9 veces menos memoria pico con el bucle, porque no materializa
    series intermedias de texto. La salida es idéntica (verificado con assert_frame_equal).
    """

    def __init__(self, columna="amenities", patrones=None):
        super().__init__(columna)
        self.patrones = dict(patrones or {})
        self._compilados = {nombre: re.compile(patron) for nombre, patron in self.patrones.items()}

    @staticmethod
    def _a_lista(texto):
        if isinstance(texto, list):
            return texto
        if texto is None or (isinstance(texto, float) and np.isnan(texto)):
            return []
        try:
            return json.loads(texto)
        except (TypeError, json.JSONDecodeError):
            return []

    def aprender(self, df):
        listas = df[self.columna].apply(self._a_lista)
        return {"indicadores": list(self.patrones),
                "mediana_comodidades_en_ajuste": float(listas.str.len().median()) if len(df) else 0.0}

    def aplicar(self, df):
        columnas = ["n_comodidades"] + list(self.patrones)
        filas = []
        for texto in df[self.columna]:
            lista = self._a_lista(texto)
            unido = "|".join(map(str, lista)).lower()
            filas.append([len(lista)] + [int(bool(p.search(unido))) for p in self._compilados.values()])
        nuevas = pd.DataFrame(filas, columns=columnas, index=df.index, dtype="int64")
        df = df.drop(columns=[self.columna])
        for columna in columnas:
            df[columna] = nuevas[columna]
        return df


class CodificadorNominal(Transformador):
    """One-hot con vocabulario aprendido en el ajuste (F2 §4.2).

    Una categoría que solo aparece en prueba NO genera columna nueva: el
    modelo no pudo aprender de ella. Los nombres son `<prefijo>_<categoria>`.
    """

    def __init__(self, columna, prefijo=None):
        super().__init__(columna)
        self.prefijo = prefijo or columna

    @staticmethod
    def _etiqueta(categoria):
        return str(categoria).strip().replace(" ", "_")

    def aprender(self, df):
        return {"categorias": sorted(df[self.columna].dropna().unique().tolist())}

    def aplicar(self, df):
        original = df[self.columna]
        df = df.drop(columns=[self.columna])
        for categoria in self._parametros["categorias"]:
            df[f"{self.prefijo}_{self._etiqueta(categoria)}"] = (original == categoria).astype(int)
        # F2 reinició el índice al codificar; se replica para que la salida sea idéntica
        return df.reset_index(drop=True)


# ============================================================================
# Escalamiento (F2, sección 5)
# ============================================================================
class EscaladorRobusto(Transformador):
    """Mediana 0 y rango intercuartílico 1 (RobustScaler), la decisión de F2 §5."""

    def __init__(self, columnas):
        super().__init__(list(columnas))

    def aprender(self, df):
        escalador = RobustScaler().fit(df[self.columna])
        return {"centro": dict(zip(self.columna, map(float, escalador.center_))),
                "escala": dict(zip(self.columna, map(float, escalador.scale_)))}

    def aplicar(self, df):
        centro = np.array([self._parametros["centro"][c] for c in self.columna])
        escala = np.array([self._parametros["escala"][c] for c in self.columna])
        # copy=True: con copy-on-write (pandas >= 3) to_numpy puede devolver una vista
        # de solo lectura y la operación en sitio fallaría.
        valores = df[self.columna].to_numpy(dtype="float64", copy=True)
        valores -= centro                     # mismo orden de operaciones que RobustScaler.transform
        valores /= escala
        df[self.columna] = valores
        return df


class EscaladorEstandar(Transformador):
    """Media 0 y desviación 1 (StandardScaler). Se conserva para COMPARAR con el robusto."""

    def __init__(self, columnas):
        super().__init__(list(columnas))

    def aprender(self, df):
        escalador = StandardScaler().fit(df[self.columna])
        return {"media": dict(zip(self.columna, map(float, escalador.mean_))),
                "desviacion": dict(zip(self.columna, map(float, escalador.scale_)))}

    def aplicar(self, df):
        media = np.array([self._parametros["media"][c] for c in self.columna])
        desv = np.array([self._parametros["desviacion"][c] for c in self.columna])
        df[self.columna] = (df[self.columna].to_numpy(dtype="float64") - media) / desv
        return df
