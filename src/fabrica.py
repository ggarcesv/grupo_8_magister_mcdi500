"""Fábrica de pipelines (patrón Factory): decide QUÉ transformador construir.

Dos constructores:
* `construir_pipeline_f2()`: el pipeline canónico, paso a paso, en el orden
  exacto de la Fase 2. Es la referencia contra la que se verifica todo.
* `construir_desde_diccionario(diccionario)`: construye los pasos de
  transformación leyendo el ROL ANALÍTICO de `docs/diccionario_variables.csv`
  (el entregable de la Fase 1), de modo que el diccionario deje de ser
  documentación y pase a gobernar el código.
"""

from . import config as cfg
from .pipeline import Pipeline
from .transformadores import (AcotadorSuperior, CodificadorNominal, ConvertidorMoneda,
                              EliminadorNulos, EscaladorRobusto, ExtractorComodidades,
                              FiltroCategoria, FiltroCoherencia, FiltroMaximo,
                              ImputadorMediana, SelectorColumnas)


def pasos_delimitacion_y_limpieza():
    """Pasos 1-13 del pipeline de la Fase 2 (secciones 3a-3e), en su orden."""
    pasos = [
        FiltroCategoria(cfg.COLUMNA_FILTRO, cfg.VALOR_FILTRO),          # 3a
        SelectorColumnas(cfg.VARIABLES_ESTUDIO),                         # 3a
        ConvertidorMoneda("price"),                                      # §2 (price como texto)
        AcotadorSuperior("maximum_nights", cfg.TOPE_MAXIMUM_NIGHTS),     # 3b
        EliminadorNulos(cfg.OBJETIVOS),                                  # 3c
    ]
    for columna in cfg.COLUMNAS_IMPUTAR:                                 # 3e
        pasos.append(ImputadorMediana(columna, bandera=(columna == cfg.COLUMNA_CON_BANDERA)))
    pasos += [
        FiltroMaximo("price", cfg.UMBRAL_PRECIO),                        # 3d
        FiltroCoherencia("bedrooms", "accommodates"),                    # 3d
    ]
    return pasos


def pasos_transformacion():
    """Pasos de la sección 4 y 5 de la Fase 2."""
    pasos = [ExtractorComodidades("amenities", cfg.COMODIDADES)]         # 4.1
    for columna, prefijo in cfg.NOMINALES.items():                       # 4.2
        pasos.append(CodificadorNominal(columna, prefijo))
    pasos.append(EscaladorRobusto(cfg.COLUMNAS_ESCALAR))                 # 5
    return pasos


def construir_pipeline_f2(clase_pipeline=Pipeline):
    """El pipeline completo de la Fase 2 como objetos. `clase_pipeline` permite
    inyectar un PipelineObservable sin cambiar nada más (bajo acoplamiento)."""
    return clase_pipeline(pasos_delimitacion_y_limpieza() + pasos_transformacion())


# ---------------------------------------------------------------------------
# Factory propiamente tal: del rol analítico al transformador
# ---------------------------------------------------------------------------
def crear_transformador(rol_analitico, columna):
    """Devuelve el transformador de la sección 4 que corresponde al rol del diccionario."""
    rol = str(rol_analitico).strip().lower()
    if rol == "texto libre" and columna in cfg.EXPLICATIVAS["comodidades"]:
        return ExtractorComodidades(columna, cfg.COMODIDADES)
    if rol in ("nominal", "binaria"):
        return CodificadorNominal(columna, cfg.NOMINALES.get(columna, columna))
    if rol in ("continua", "discreta"):
        return None          # las numéricas se imputan en limpieza y se escalan al final
    raise ValueError(
        f"Rol '{rol_analitico}' de la variable '{columna}' no tiene transformador asignado. "
        "Roles admitidos: texto libre (amenities), nominal, binaria, continua, discreta."
    )


def construir_desde_diccionario(diccionario, clase_pipeline=Pipeline):
    """Construye el pipeline leyendo el rol analítico de cada explicativa del diccionario.

    Parámetros
    ----------
    diccionario : pd.DataFrame con columnas 'variable' y 'rol_analitico'
        (docs/diccionario_variables.csv, Fase 1).
    """
    roles = dict(zip(diccionario["variable"], diccionario["rol_analitico"]))
    explicativas = [v for grupo in cfg.EXPLICATIVAS.values() for v in grupo]
    faltan = [v for v in explicativas if v not in roles]
    if faltan:
        raise KeyError(f"El diccionario no declara el rol de: {faltan}")

    creados = {v: crear_transformador(roles[v], v) for v in explicativas}
    creados = {v: p for v, p in creados.items() if p is not None}

    # Mismo orden que la Fase 2: primero las comodidades, luego los bloques one-hot
    # en el orden declarado en config.NOMINALES (superhost antes que comuna).
    extractores = [p for p in creados.values() if isinstance(p, ExtractorComodidades)]
    codificadores = [creados[v] for v in cfg.NOMINALES if v in creados]
    otros = [p for v, p in creados.items()
             if not isinstance(p, ExtractorComodidades) and v not in cfg.NOMINALES]

    pasos = pasos_delimitacion_y_limpieza() + extractores + codificadores + otros
    pasos.append(EscaladorRobusto(cfg.COLUMNAS_ESCALAR))
    return clase_pipeline(pasos)
