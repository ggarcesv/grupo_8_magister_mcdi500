import numpy as np
import pandas as pd
import timeit

def medir(funcion, *args, **kwargs):
    """Ejecuta la función una vez y devuelve (resultado, segundos, memoria pico en MB)."""
    tracemalloc.start()                       # empieza a vigilar la memoria
    inicio = time.perf_counter()
    resultado = funcion(*args, **kwargs)
    segundos = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory() # el máximo de memoria que se usó
    tracemalloc.stop()
    return resultado, segundos, pico / 1024 / 1024


# Datos reales justo antes de escalar: todos los pasos del pipeline menos los escaladores
pasos_previos = [p for p in construir_pipeline().pasos_ejecutados()
                 if not isinstance(p, EscaladorRobusto)]
antes_de_escalar = datos.copy()
for paso in pasos_previos:
    antes_de_escalar = paso.ajustar_transformar(antes_de_escalar)

escalador = EscaladorRobusto("n_comodidades").ajustar(antes_de_escalar)
MEDIANA, RIC = escalador.parametros["mediana"], escalador.parametros["ric"]


def escalar_con_bucle(serie):
    """Versión A: valor por valor, con un for."""
    escalados = []
    for valor in serie:
        escalados.append((valor - MEDIANA) / RIC)
    return escalados


def escalar_vectorizado(serie):
    """Versión B: toda la columna de una vez (la que usa EscaladorRobusto)."""
    return ((serie - MEDIANA) / RIC).tolist()


serie = antes_de_escalar["n_comodidades"]

# Antes de comparar tiempos: las dos deben dar EXACTAMENTE lo mismo
assert escalar_con_bucle(serie) == escalar_vectorizado(serie), "Las versiones no coinciden"
print(f"Las dos versiones dan el mismo resultado sobre los {len(serie)} alojamientos.\n")