"""Herramienta de medición de tiempo y memoria.

Los experimentos (qué se mide y cómo se interpreta) viven en el notebook;
aquí solo está la función reutilizable.
"""
import time
import tracemalloc


def medir(funcion, *args, **kwargs):
    """Ejecuta la función una vez y devuelve (resultado, segundos, memoria pico en MB).

    tracemalloc registra la memoria que Python reserva mientras corre la función;
    get_traced_memory() entrega la actual y la máxima (pico). Interesa el pico.
    *args y **kwargs reenvían a la función los argumentos que reciba.
    """
    tracemalloc.start()
    inicio = time.perf_counter()
    resultado = funcion(*args, **kwargs)
    segundos = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, segundos, pico / 1024 / 1024
