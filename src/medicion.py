"""Medición reproducible de tiempo y memoria (timeit + tracemalloc)."""

import timeit
import tracemalloc

import pandas as pd


def medir(funcion, *args, repeticiones=5, numero=1, **kwargs):
    """Mide una función. Devuelve (resultado, segundos_min, memoria_pico_MB).

    * Tiempo: `timeit.repeat` y se conserva el MÍNIMO, no el promedio. Los valores
      altos reflejan interrupciones del sistema operativo, no el costo del código.
    * Memoria: `tracemalloc` registra el pico de asignaciones durante UNA ejecución.
    """
    tiempos = timeit.repeat(lambda: funcion(*args, **kwargs), repeat=repeticiones, number=numero)
    segundos = min(tiempos) / numero

    tracemalloc.start()
    resultado = funcion(*args, **kwargs)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, segundos, pico / (1024 ** 2)


def comparar_implementaciones(implementaciones, generar_datos, tamanos,
                              repeticiones=5, numero=1, verificar_igualdad=None):
    """Compara varias implementaciones sobre varios tamaños. Devuelve un DataFrame.

    Parámetros
    ----------
    implementaciones : dict nombre -> función(datos)
    generar_datos : función(n) -> datos de tamaño n
    tamanos : iterable de n
    verificar_igualdad : función(a, b) -> bool, para comprobar que todas devuelven lo mismo
    """
    filas = []
    for n in tamanos:
        datos = generar_datos(n)
        salidas = {}
        for nombre, funcion in implementaciones.items():
            salida, segundos, memoria = medir(funcion, datos, repeticiones=repeticiones, numero=numero)
            salidas[nombre] = salida
            filas.append({"n": n, "implementacion": nombre,
                          "ms": round(segundos * 1000, 3), "memoria_pico_MB": round(memoria, 3)})
        if verificar_igualdad is not None:
            referencia = next(iter(salidas.values()))
            for nombre, salida in salidas.items():
                if not verificar_igualdad(referencia, salida):
                    raise AssertionError(f"'{nombre}' no coincide con la referencia para n={n}.")
    tabla = pd.DataFrame(filas)
    base = tabla.groupby("n")["ms"].transform("max")
    tabla["veces_mas_rapida_que_la_peor"] = (base / tabla["ms"]).round(1)
    return tabla
