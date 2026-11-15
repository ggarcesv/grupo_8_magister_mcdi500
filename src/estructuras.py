"""Funciones recursivas sobre estructuras anidadas de profundidad desconocida."""


def aplanar(estructura, prefijo="", separador="."):
    """Aplana un diccionario anidado en pares 'ruta.clave' -> valor.

    Caso base: el valor no es un diccionario -> se guarda el par.
    Caso recursivo: el valor es un diccionario -> se desciende con el prefijo extendido.

    >>> aplanar({"a": {"b": 1, "c": {"d": 2}}})
    {'a.b': 1, 'a.c.d': 2}
    """
    plano = {}
    for clave, valor in estructura.items():
        ruta = f"{prefijo}{separador}{clave}" if prefijo else str(clave)
        if isinstance(valor, dict) and valor:
            plano.update(aplanar(valor, ruta, separador))
        elif isinstance(valor, (list, tuple)):
            plano[ruta] = ", ".join(str(v) for v in valor)
        else:
            plano[ruta] = valor
    return plano


def profundidad(estructura):
    """Profundidad máxima de anidamiento de un diccionario (0 si no es dict)."""
    if not isinstance(estructura, dict) or not estructura:
        return 0
    return 1 + max(profundidad(v) for v in estructura.values())
