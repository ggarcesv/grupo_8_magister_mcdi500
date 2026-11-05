# Análisis de Inversión en Airbnb — Grupo 8

una breve descripcion del problema a resolver...

## Integrantes
- Cristopher Contreras (@usuario-github)
- Gabriel Cruz (@usuario-github)
- Giuliano Garces (@usuario-github)
- Ana Hermosilla (@usuario-github)


## Datos
- Fuente: Stroke Prediction Dataset (fedesoriano, Kaggle)
- Enlace: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
- Estructura: 5110 filas x 12 columnas
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

Ejecutar los cuadernos en orden, F1 y luego F2. Cada cuaderno localiza la raíz del
proyecto aunque Jupyter lo abra en su propia carpeta.

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
