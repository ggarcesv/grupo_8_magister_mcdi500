# Estudio de Inversión Inmobiliaria Airbnb — Grupo 8

El objetivo principal es resolver la siguiente problemática:

¿Qué características de los alojamientos publicados en Airbnb se asocian con diferencias en sus precios y niveles de ocupación estimada, y cómo pueden estos hallazgos orientar a potenciales nuevos anfitriones?

El análisis se centra en identificar variables clave como ubicación (comuna), tipo de propiedad, comodidades y características del anfitrión, para determinar su impacto en el precio (tarifas) y el desempeño (ocupación anual estimada e ingresos).

## Integrantes
- Cristopher Contreras (@cristopherconar )
- Gabriel Cruz (@gcruzstm-gif)
- Giuliano Garces (@ggarcesv)
- Ana Hermosilla (@Ana-Hermosilla)


<<<<<<< HEAD
## Datos
- Fuente: Stroke Prediction Dataset (fedesoriano, Kaggle)
- Enlace: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
- Estructura: 32598 filas x 90 columnas
- Ubicación esperada: `data/raw/`

## Estructura del repositorio
```
data/raw/        datos originales, sin modificar
data/processed/  datos tras limpieza y transformación (F2)
docs/            diccionario, fichas y metadatos
src/             módulos reutilizables del proyecto
F1/ F2/ F3/ F4/  cuadernos e informes de cada fase
```

## Requisitos y ejecución
Python 3.13

    python -m venv .venv
    source .venv/Scripts/activate    # Windows, Git Bash
    # source .venv/bin/activate      # macOS y Linux
    python -m pip install -r requirements.txt

Ejecutar los cuadernos en orden, F1 y luego F2. Cada cuaderno localiza la raíz del proyecto aunque Jupyter lo abra en su propia carpeta.

### Dependencias declaradas
- ipykernel
- jupyterlab
- notebook
- numpy==2.5.4
- pandas==3.1.0

## Convención de commits
Prefijos usados: docs, data, feat, fix.

## Decisiones técnicas
- Los datos son comunes a todas las fases (`data/`); los cuadernos se separan por fase.
- Semilla aleatoria fijada en 42 para asegurar reproducibilidad.
- Registro breve de las decisiones relevantes y su motivo, actualizado al cerrar cada fase.
=======
# Hola Gabriel soy Anita
>>>>>>> 3e24155db53da628b921d833288176e7ca8ba0f7
