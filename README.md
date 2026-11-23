# Caracterización de precios y ocupación estimada en Airbnb en Santiago de Chile — Grupo 8

Problemática principal: ¿Qué relación existe entre las comodidades, la capacidad de alojamiento y la ubicación de los alojamientos completos publicados en Airbnb Santiago con sus precios y niveles de ocupación anual estimada?

El análisis tendrá un enfoque descriptivo y exploratorio. No pretende establecer relaciones causales ni determinar la rentabilidad de los alojamientos.

## Integrantes

- Cristopher Contreras (@cristopherconar)
- Gabriel Cruz (@gcruzstm-gif)
- Giuliano Garces (@ggarcesv)
- Ana Hermosilla (@Ana-Hermosilla)

## Datos

* Fuente: [Inside Airbnb](https://insideairbnb.com/)
* Enlace: https://data.insideairbnb.com/chile/rm/santiago/2026-09-23/data/listings.csv.gz
* Captura: 23 de septiembre de 2026
* Estructura: 18904 filas × 90 columnas
* Ubicación esperada: `data/raw/datasetairbnb.csv`
* Integridad: el archivo se verifica con su huella SHA-256: CF7BC651740CAB3B29B5BF069728E36FA9A33E0306BBFF4DEDD84A42D6389FC4 



## Estructura del repositorio

```
data/raw/           datos originales, sin modificar (excluidos de Git)
data/processed/     artefactos de F2 y F3 (dataset procesado, partición y parámetros)
docs/               diccionario de variables, metadatos, validación del dataset y hallazgos de F4
src/                módulos reutilizables del proyecto
F1/ F2/ F3/ F4/     notebook de cada fase
F4/figuras/         figuras finales exportadas por el notebook F4
requirements.txt    dependencias con versiones fijas
```

## Fases

|Fase|Notebook|Entrega a la fase siguiente|
|-|-|-|
|F1 · Definición|Problema y objetivos, entorno, procedencia y huella del dataset|Ficha del dataset y metadatos|
|F2 · Preprocesamiento|Exploración, limpieza, imputación comparada, comodidades y One-Hot|`airbnb\_procesado.csv` (14.758 × 50)|
|F3 · Núcleo algorítmico|Clases, pipeline, validación contra F2, recursividad, eficiencia y patrón Strategy|Cuatro artefactos en `data/processed/`|
|F4 · Comunicación|Copia interpretable verificada, figuras, eficiencia y validación|Figuras en `F4/figuras/` y `docs/hallazgos\_f4.csv`|


## Módulos  de `src/`

|Módulo|Responsabilidad|
|-|-|
|`carga.py`|Lectura del CSV y validación estricta del esquema|
|`transformadores.py`|Clase base `Transformador` y sus once clases hijas de limpieza y transformación|
|`estrategias.py`|Patrón Strategy para la imputación: `EstrategiaImputacion`, `PorMediana`, `PorMedia`, `PorMedianaDeGrupo`|
|`pipeline.py`|Clase `Pipeline` que encadena los pasos y `construir\_pipeline(config)` que los crea desde la configuración|
|`medicion.py`|Medición reproducible de tiempo (`timeit`) y memoria pico (`tracemalloc`)|
|`comunicacion.py`|Copia interpretable (inversa del escalamiento), intervalos de Wilson y guardado de figuras|
|`utilidades.py`|Normalización de nombres de columnas (`normalizar\_nombre()`, `normalizar\_columnas()`) y excepción del dominio `ProyectoError`


## Requisitos y ejecución


Se utiliza Python 3.13 como versión de referencia del proyecto.

Para preparar el entorno virtual desde la raíz del repositorio:

Windows — PowerShell

```
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS o Linux

```
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Las dependencias y sus versiones se especifican en requirements.txt, que debe mantenerse compatible con los sistemas operativos utilizados por los integrantes y evaluadores.

### Dependencias declaradas

- ipykernel
- jupyterlab
- notebook
- numpy==2.5.4
- pandas==3.1.1

## Instrucciones para reproducir el proyecto

1. Clonar el repositorio.
2. Crear el entorno virtual e instalar las dependencias indicadas en requirements.txt.
3. Descargar el archivo listings.csv.gz desde el enlace indicado, descomprimirlo y guardar el archivo como `data/raw/datasetairbnb.csv`.
4. Abrir Jupyter Lab o VSCode con el kernel del entorno virtual.
5. Ejecutar los notebooks en orden **F1 → F2 → F3 → F4**, cada uno con *Restart Kernel and Run All*. Cada notebook comprueba que se ejecuta dentro del entorno virtual, y F4 se detiene con un mensaje claro si faltan los artefactos de F3.


Usen solo la captura del 23 de septiembre de 2026: otras versiones pueden tener otra cantidad de registros, otras variables y otros valores. Si la huella SHA-256 no coincide, el notebook lo informa.


## Convención de commits

Prefijos usados:

- docs: modificar documentación
- data: Incorporar o actualizar datos
- feat: incorporar una funcionalidad nueva
- fix: corregir errores o problemas

## Decisiones técnicas

* **Datos originales fuera de Git.** El archivo contiene información potencialmente identificable de los anfitriones (nombres, descripciones y enlaces a perfiles). Por eso `data/raw/` está excluida mediante `.gitignore` y cada integrante descarga el archivo desde la fuente. Solo se versionan datos procesados que no contienen información personal.
* **Alcance.** Se analizan solo alojamientos completos (*Entire home/apt*): 15.383 anuncios, que quedan en 14.758 tras la limpieza.
* **Reproducibilidad.** Semilla aleatoria fija (42) y partición entrenamiento/prueba 80/20 sin fuga de datos.
* **Clases donde se aprende algo de los datos.** Los pasos que aprenden parámetros del entrenamiento son clases con un contrato común (`ajustar()` / `transformar()`). Las operaciones que no aprenden nada son funciones.
* **Patrón Strategy en la imputación.** Permite cambiar entre mediana, media y mediana por grupo sin reescribir el imputador. Se eligió la mediana: las tres estrategias cambian la desviación de `beds` en menos de 1 % y la mediana es la más simple y coherente con la asimetría de los datos.
* **Vectorización.** El escalamiento vectorizado es 41,1 veces más rápido que el bucle `for` y usa 0,18 veces su memoria. Una medición anterior registraba un 24 % más de memoria, pero esa cifra medía una conversión a lista y no el escalador, y se corrigió en F3.
* **Extractor de comodidades.** Es el paso más costoso del pipeline (82 % del tiempo). Se mantiene la versión con `json` porque detecta filas mal formadas, aunque usa más memoria que la versión sin `json`.

