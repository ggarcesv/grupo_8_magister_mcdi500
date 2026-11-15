"""Paquete de módulos reutilizables del proyecto MCDI500 · Grupo 8.

Organización (alta cohesión, bajo acoplamiento):

    config.py          declara QUÉ variables y umbrales usa el estudio (sin código de proceso)
    carga.py           solo lee el archivo y verifica su esquema
    transformadores.py la clase base Transformador y sus hijas (un paso = una clase)
    pipeline.py        solo encadena pasos y controla el orden ajustar -> transformar
    observadores.py    bitácora que escucha al pipeline (patrón Observer)
    fabrica.py         construye transformadores desde el diccionario de variables (Factory)
    medicion.py        mide tiempo y memoria de cualquier función (timeit + tracemalloc)

El cuaderno de la Fase 3 importa estos módulos; no los reescribe.
"""
