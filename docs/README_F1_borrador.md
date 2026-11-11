# Relación entre características de alojamientos frente a precios y niveles de ocupación en Airbnb — Grupo 8

Los anfitriones de Airbnb desconocen cómo se relacionan ciertas caracterísiticas de los alojamientos frente al precio y niveles de ocupación. Acceder a esta información puede ser de utilidad para quienes ya cuenten con un alojamiento publicado o para quienes estén considerando entrar al mercado de Airbnb. Sin embargo, la información relevante se encuentra distribuida entre numerosos anuncios. Este proyecto busca organizar y describir dichas características mediante datos públicos de Airbnb en Santiago de Chile.

## Integrantes
- Giuliano Garces (@usuario-github)
- Ana Hermosilla (@usuario-github)
- Cristopher Contreras (@usuario-github)
- Gabriel Cruz (@usuario-github)

## Datos
- Fuente: Inside Airbnb - Santiago, Chile (Murray Cox (Inside Airbnb), Inside Airbnb)
- Enlace: https://data.insideairbnb.com/chile/rm/santiago/2026-09-23/data/listings.csv.gz
- Estructura: 18904 filas x 90 columnas
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
- numpy==2.5.4
- pandas==3.1.0
- matplotlib==3.11.2
- scikit-learn==1.9.1
- ipython==9.18.1
- ipykernel==7.4.0
- jupyterlab==4.6.5
- notebook==7.6.4

## Convención de commits
Prefijos usados: docs, data, feat, fix.

## Decisiones técnicas
- Los datos son comunes a todas las fases (`data/`); los cuadernos se separan por fase.
- Semilla aleatoria fijada en 42 para asegurar reproducibilidad.
- Registro breve de las decisiones relevantes y su motivo, actualizado al cerrar cada fase.
