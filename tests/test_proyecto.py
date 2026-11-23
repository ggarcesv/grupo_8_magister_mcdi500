
import numpy as np
import pandas as pd
import pytest

from src import comunicacion as com
from src import transformadores as tr


# ---------------------------------------------------------------- escalamiento
def test_revertir_escalamiento_devuelve_valores_originales():
    """x = z * RIC + mediana, con números que se pueden verificar a mano."""
    escalado = pd.DataFrame({"accommodates": [-1.0, 0.0, 0.5, 2.0]})
    parametros = {"EscaladorRobusto(accommodates)": {"mediana": 3.0, "ric": 2.0}}

    resultado = com.revertir_escalamiento(escalado, parametros)

    assert resultado["accommodates"].tolist() == [1.0, 3.0, 4.0, 7.0]


def test_escalar_y_revertir_es_ida_y_vuelta():
    """Ajustar el escalador, transformar y revertir recupera los datos originales."""
    original = pd.DataFrame({"accommodates": [1.0, 2.0, 3.0, 4.0, 10.0]})
    paso = tr.EscaladorRobusto("accommodates").ajustar(original)
    escalado = paso.transformar(original)

    parametros = {"EscaladorRobusto(accommodates)": paso.parametros}
    revertido = com.revertir_escalamiento(escalado, parametros)

    np.testing.assert_allclose(revertido["accommodates"], original["accommodates"])


def test_transformar_no_modifica_el_dataframe_recibido():
    original = pd.DataFrame({"accommodates": [1.0, 2.0, 3.0]})
    copia = original.copy()
    tr.EscaladorRobusto("accommodates").ajustar(original).transformar(original)
    pd.testing.assert_frame_equal(original, copia)


# ---------------------------------------------------------------- Wilson
def test_wilson_valor_conocido():
    """5 de 10 con 95 %: intervalo de Wilson (0,2366; 0,7634)."""
    inferior, superior = com.intervalo_wilson(5, 10)
    assert inferior == pytest.approx(0.2366, abs=1e-4)
    assert superior == pytest.approx(0.7634, abs=1e-4)


def test_wilson_extremos_quedan_entre_0_y_1():
    """Con 0 o n casos el intervalo no se sale de [0, 1] (Wald sí lo haría)."""
    inf0, sup0 = com.intervalo_wilson(0, 10)
    infn, supn = com.intervalo_wilson(10, 10)
    assert inf0 == pytest.approx(0.0, abs=1e-9) and sup0 == pytest.approx(0.2775, abs=1e-4)
    assert infn == pytest.approx(0.7225, abs=1e-4) and supn == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------- excepciones
def test_transformar_sin_ajustar_lanza_error():
    with pytest.raises(RuntimeError, match="ajustar"):
        tr.EscaladorRobusto("accommodates").transformar(pd.DataFrame({"accommodates": [1, 2]}))


def test_ajustar_con_columna_inexistente_lanza_keyerror():
    with pytest.raises(KeyError):
        tr.EscaladorRobusto("no_existe").ajustar(pd.DataFrame({"accommodates": [1, 2]}))


def test_parametros_con_json_incompleto_lanza_valueerror():
    malo = pd.DataFrame([{"paso": "EscaladorRobusto(accommodates)", "parametros": '{"mediana": '}])
    with pytest.raises(ValueError):
        com.leer_parametros(malo)


def test_falta_un_artefacto_lanza_filenotfounderror(tmp_path):
    with pytest.raises(FileNotFoundError):
        com.cargar_artefactos(tmp_path / "carpeta_vacia")
