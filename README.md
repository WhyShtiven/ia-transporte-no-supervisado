# Predicción de ocupación en transporte masivo con árboles de decisión

**Actividad 3 – Aprendizaje supervisado** · Inteligencia Artificial · Corporación Universitaria Iberoamericana · Docente: Sandra Bautista

Integrantes: Freddy Anderson Lombana Cárdenas · Miller Guayabo Sánchez · Javier Shtiven Chaparro Hernández

Continúa el proyecto de transporte masivo de la Actividad 2 (líneas B1, B2, C1, D1, E1). Aquí se entrena un **árbol de decisión** que clasifica la ocupación de una estación en `bajo`, `medio` o `alto`.

## Contenido

| Archivo | Descripción |
|---|---|
| `datos/ocupacion_transporte.csv` | Dataset (5 000 registros, sintético) |
| `generar_dataset.py` | Genera el dataset de forma reproducible |
| `modelo_arbol_decision.py` | Limpieza, entrenamiento, evaluación y guardado del modelo |
| `pruebas_modelo.py` | 16 pruebas automatizadas |
| `DESCRIPCION_DATOS.md` | Fuentes, diccionario de datos y análisis exploratorio |
| `PRUEBAS.md` | Pruebas realizadas y métricas |
| `GUION_VIDEO.md` | Guion y reparto para el video |
| `resultados/` | Gráficas, reglas del árbol, métricas, modelo guardado y salida de pruebas |

## Ejecución

Requiere Python 3.9 o superior.

```bash
pip install -r requirements.txt
python generar_dataset.py            # crea datos/ocupacion_transporte.csv
python modelo_arbol_decision.py      # entrena y guarda resultados/
python -m unittest pruebas_modelo -v # corre las 16 pruebas
```

## Resultados

| Métrica | Valor |
|---|---|
| Exactitud en prueba | 83,4 % |
| Validación cruzada (5-fold) | 83,4 % ± 0,8 |
| Modelo base (clase mayoritaria) | 34,4 % |

La variable más influyente es la hora del día, seguida de los buses por hora, si es fin de semana, la lluvia y los eventos especiales.

> Los datos son sintéticos (ver `DESCRIPCION_DATOS.md`): las métricas validan el flujo de trabajo, no el desempeño con datos reales.

## Uso del modelo guardado

```python
import joblib, pandas as pd

paquete = joblib.load("resultados/modelo_arbol.joblib")
modelo, columnas = paquete["modelo"], paquete["columnas"]

fila = pd.DataFrame([{c: 0 for c in columnas}])
fila["hora"] = 7; fila["dia_semana"] = 1; fila["llueve"] = 1
fila["temperatura_c"] = 14.0; fila["buses_por_hora"] = 12
fila["estacion_Portal Norte"] = 1; fila["linea_B1"] = 1; fila["zona_portal"] = 1
print(modelo.predict(fila)[0])   # -> alto
```

## Trabajo en equipo con Git

El log del repositorio debe mostrar el aporte de cada integrante, así que **cada uno debe hacer sus propios commits desde su cuenta**. Sugerencia de reparto:

- Integrante 1: `generar_dataset.py`, `DESCRIPCION_DATOS.md`
- Integrante 2: `modelo_arbol_decision.py`, `requirements.txt`
- Integrante 3: `pruebas_modelo.py`, `PRUEBAS.md`, `GUION_VIDEO.md`

Cada quien trabaja en su rama, hace `git commit -m "mensaje claro"`, abre un *pull request* y lo fusionan en `main`. No olviden agregar a la docente como colaboradora del repositorio (Settings → Collaborators / Project members).
