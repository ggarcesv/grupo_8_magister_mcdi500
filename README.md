# Caracterización de precios y ocupación estimada en Airbnb en Santiago de Chile — Grupo 8

Problemática principal: ¿Qué relación existe entre las comodidades, la capacidad de alojamiento y la ubicación de los alojamientos completos publicados en Airbnb Santiago con sus precios y niveles de ocupación anual estimada?

El análisis tendrá un enfoque descriptivo y exploratorio. No pretende establecer relaciones causales ni determinar la rentabilidad de los alojamientos.

## Integrantes

- Cristopher Contreras (@cristopherconar)
- Gabriel Cruz (@gcruzstm-gif)
- Giuliano Garces (@ggarcesv)
- Ana Hermosilla (@Ana-Hermosilla)

## Datos

- Fuente: [Inside Airbnb]
- Enlace: https://data.insideairbnb.com/chile/rm/santiago/2026-09-23/data/listings.csv.gz
- Estructura: 18904 filas × 90 columnas
- Ubicación esperada: `data/raw/datasetairbnb.csv`
- La integridad del dataset original se realiza mediante algoritmo SHA-256, Huella SHA-256: CF7BC651740CAB3B29B5BF069728E36FA9A33E0306BBFF4DEDD84A42D6389FC4 

## Estructura del repositorio

```
data/raw/        datos originales, sin modificar
data/processed/  datos tras limpieza y transformación (F2)
docs/            diccionario, fichas y metadatos
src/             módulos reutilizables del proyecto
F1/ F2/ F3/ F4/  cuadernos e informes de cada fase
```

## Módulos

```
src/carga.py: lectura de archivos externos y validación estricta de esquema. 
src/transformadores.py: definición de la clase base abstracta Transformador, sus diez clases hijas de limpieza/transformación y la excepción personalizada del dominio (ProyectoError). 
src/pipeline.py: orquestación secuencial mediante Pipeline y construcción parametrizada desde construir_pipeline(config). 
src/medicion.py: perfilado reproducible de tiempo de ejecución (timeit) y consumo de memoria pico (tracemalloc).
src/estrategias.py: implementación del patrón Strategy para imputación de nulos mediante clases intercambiables (EstrategiaImputacion, PorMediana, PorMedia, PorMedianaDeGrupo).
src/utilidades.py: utilidades transversales generadas desde la Fase 1 para estandarizar nombres de columnas sin duplicados (normalizar_nombre(), normalizar_columnas()) y definir la excepción personalizada del dominio (ProyectoError).
```

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

## Instrucciones para reproducir el proyecto

Clonar el repositorio de GitHub.

Crear el entorno virtual e instalar las dependencias indicadas en requirements.txt.

Descargar el archivo listings.csv.gz desde el enlace indicado.

Descomprimir el archivo para obtener listings.csv.

Renombrar el archivo descomprimido como datasetairbnb.csv.

Guardarlo en la carpeta data/raw/ del repositorio.

Ejecutar los notebooks oficiales, comenzando por F1 y posteriormente F2.

La ruta esperada por los notebooks es:

data/raw/datasetairbnb.csv

Asegurar que el data set descargado corresponda a la captura del 23 de septiembre de 2026, versiones distintas a esta pueden poseer otras características que no son contempladas para la ejecución de este proyecto.

### Dependencias declaradas

- ipykernel
- jupyterlab
- notebook
- numpy==2.5.4
- pandas==3.1.1

## Convención de commits

Prefijos usados:

- docs: modificar documentación
- data: Incorporar o actualizar datos
- feat: incorporar una funcionalidad nueva
- fix: corregir errores o problemas

## Decisiones técnicas

El archivo original contiene información potencialmente identificable de los anfitriones, como nombres, descripciones y enlaces a perfiles. Por esta razón, no se distribuye ni versiona en este repositorio.

La carpeta data/raw/ está excluida del seguimiento de Git mediante .gitignore. Cada usuario debe obtener el dataset desde la fuente original y conservarlo localmente.

La ejecución de F1 requiere que el archivo esté disponible en la ubicación y con el nombre especificados, ya que las auditorías del diccionario de variables y las comprobaciones de calidad leen directamente sus contenidos.
Se debe utilizar la versión correspondiente a la captura documentada, porque otras versiones pueden presentar diferencias en la cantidad de registros, las variables y sus valores.

El repositorio podrá incluir datos procesados únicamente después de verificar que no contengan información personal identificable.
Los datos son comunes a todas las fases (`data/`); los cuadernos se separan por fase.

Semilla aleatoria fijada en 42 para asegurar reproducibilidad.
Registro breve de las decisiones relevantes y su motivo, actualizado al cerrar cada fase.

Se ha decidido trabajar en el proyecto en base a programación orientada objetos a través de la modularidad con cuatro módulos de Python dentro de /src. Como decisión de optimización, se adoptó el procesamiento vectorizado con pandas para el escalamiento de variables, obteniendo una ejecución aproximadamente 5 veces más rápida que la versión iterativa con for, aunque con un consumo de memoria un 24 % mayor. Esta arquitectura favorece la reutilización, trazabilidad y mantenimiento del código para las siguientes fases del proyecto.
