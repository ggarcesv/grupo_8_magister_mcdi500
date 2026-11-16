class Transformador:
    """Clase base: lo que todos los pasos del pipeline de Airbnb comparten.

    Esta clase NO se usa directamente. Su trabajo es definir el contrato:
    qué métodos tendrá todo paso del pipeline y cómo se controla su estado.
    Las clases hijas solo completan lo que cambia de un paso a otro.
    """

    def __init__(self, columna):
        # Atributo público: cualquiera puede leerlo y cambiarlo
        self.columna = columna

        # Atributos con guion bajo: por convención, INTERNOS.
        # Python no lo impide, pero el guion bajo le dice a quien lee el código
        # que no debe tocarlos desde fuera de la clase.
        self._parametros = {}       # lo que el paso aprende del conjunto
        self._ajustado = False      # controla que no se transforme antes de ajustar

    # @property convierte un método en algo que se lee como atributo:
    # se escribe paso.nombre y no paso.nombre(). Y como no hay setter,
    # el valor NO se puede asignar desde fuera. Eso es encapsulamiento.
    def _columnas(self):
        """Devuelve siempre una lista, aunque se haya indicado una sola columna."""
        return [self.columna] if isinstance(self.columna, str) else list(self.columna)

    @property
    def nombre(self):
        # type(self).__name__ devuelve el nombre de la clase REAL del objeto
        etiqueta = self.columna if isinstance(self.columna, str) else ", ".join(self.columna)
        return f"{type(self).__name__}({etiqueta})"

    @property
    def parametros(self):
        # dict(...) crea una COPIA. Si devolviéramos self._parametros
        # directamente, quien lo recibe podría modificar el estado interno
        # del objeto sin que la clase se entere. A esto se le llama
        # copia defensiva.
        return dict(self._parametros)

    def ajustar(self, df):
        """Aprende los parámetros del conjunto que recibe."""
        # 1) Validar la entrada ANTES de trabajar: si algo falta, se avisa
        #    acá y no veinte líneas más abajo con un error incomprensible
        faltantes = [c for c in self._columnas() if c not in df.columns]
        if faltantes:
            raise KeyError(f"{self.nombre}: no existen las columnas {faltantes}.")

        # 2) Delegar el cálculo a la clase hija. La base no sabe QUÉ se aprende;
        #    solo sabe CUÁNDO hay que aprenderlo.
        self._parametros = self.aprender(df)

        # 3) Registrar que ya se ajustó, para poder controlarlo después
        self._ajustado = True

        # 4) Devolver self permite encadenar: paso.ajustar(df).transformar(df)
        return self

    def transformar(self, df):
        """Aplica la transformación usando lo aprendido en ajustar()."""
        # Esta guarda es el corazón del encapsulamiento: impide un uso
        # incorrecto que de otro modo pasaría inadvertido
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: hay que ajustar antes de transformar.")

        # df.copy() evita modificar el DataFrame que nos pasaron. Sin esto,
        # el objeto original del usuario cambiaría sin que él lo pidiera.
        return self.aplicar(df.copy())

    def ajustar_transformar(self, df):
        """Atajo para el caso habitual: aprender y aplicar sobre el mismo conjunto."""
        return self.ajustar(df).transformar(df)

    # ---- Métodos que cada clase hija DEBE implementar -------------------
    # Se definen acá lanzando NotImplementedError para dejar el contrato
    # explícito: si una hija olvida implementarlos, el error lo dice claro.

    def aprender(self, df):
        """Calcula y devuelve los parámetros. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aprender().")

    def aplicar(self, df):
        """Aplica la transformación. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aplicar().")


# La clase base no se usa sola
try:
    Transformador("beds").ajustar(datos)
except NotImplementedError as error:
    print("NotImplementedError:", error)