"""
generar_dataset.py
------------------
Genera un dataset SINTÉTICO (muestra) de ocupación en las estaciones del
sistema de transporte masivo del proyecto (Actividad 2: líneas B1, B2, C1, D1
y E1; Portal Norte, Calle 127, Calle 100, Calle 72, Calle 45, Av. Jimenez,
Portal Sur, Usaquen y Centro). Se usa una muestra sintética porque no se
dispone de datos reales del proyecto; la estructura imita la de los registros
de validaciones de tarjeta (torniquetes) y conteos de ocupación que publican
operadores como TransMilenio (datos abiertos de Bogotá).

Variable objetivo: nivel_ocupacion  ->  bajo | medio | alto
La relación entre variables se construye con reglas realistas + ruido, de modo
que el árbol de decisión tenga patrones por aprender, pero no sea trivial.

Uso:
    python generar_dataset.py
Salida:
    datos/ocupacion_transporte.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEMILLA = 42
N_REGISTROS = 5000
rng = np.random.default_rng(SEMILLA)

# Estaciones del sistema modelado en la Actividad 2 (sistema_transporte.py):
# (zona, peso de demanda base, líneas que atienden la estación)
ESTACIONES = {
    "Portal Norte": ("portal", 1.35, ["B1", "B2", "C1"]),
    "Calle 127":    ("norte",  0.90, ["B1", "B2", "C1", "D1"]),
    "Usaquen":      ("norte",  0.75, ["D1"]),
    "Calle 100":    ("norte",  1.10, ["B1", "B2", "C1", "D1"]),
    "Calle 72":     ("centro", 1.20, ["B1", "B2", "C1"]),
    "Calle 45":     ("centro", 1.25, ["B1", "B2", "C1", "E1"]),
    "Centro":       ("centro", 1.40, ["E1"]),
    "Av. Jimenez":  ("centro", 1.45, ["B1", "B2", "C1", "E1"]),
    "Portal Sur":   ("portal", 1.30, ["B1", "B2", "C1"]),
}

nombres = list(ESTACIONES)
estacion = rng.choice(nombres, size=N_REGISTROS)
zona = np.array([ESTACIONES[e][0] for e in estacion])
peso_estacion = np.array([ESTACIONES[e][1] for e in estacion])
# La línea observada es una de las que realmente pasan por la estación
linea = np.array([rng.choice(ESTACIONES[e][2]) for e in estacion])

hora = rng.integers(5, 23, size=N_REGISTROS)            # 5:00 a 22:00
dia_semana = rng.integers(0, 7, size=N_REGISTROS)       # 0=lunes ... 6=domingo
es_fin_de_semana = (dia_semana >= 5).astype(int)
es_festivo = (rng.random(N_REGISTROS) < 0.04).astype(int)
llueve = (rng.random(N_REGISTROS) < 0.25).astype(int)
temperatura = np.clip(rng.normal(17, 3, N_REGISTROS), 8, 28).round(1)
evento_especial = (rng.random(N_REGISTROS) < 0.05).astype(int)
buses_por_hora = rng.integers(8, 41, size=N_REGISTROS)  # frecuencia ofertada

# --- Construcción de la demanda (puntaje latente) ---
pico_manana = np.isin(hora, [6, 7, 8]).astype(float)
pico_tarde = np.isin(hora, [17, 18, 19]).astype(float)
valle = np.isin(hora, [10, 11, 12, 13, 14, 15]).astype(float)
noche = (hora >= 21).astype(float)

demanda = (
    1.0
    + 1.6 * pico_manana
    + 1.5 * pico_tarde
    + 0.2 * valle
    - 0.5 * noche
    - 0.9 * es_fin_de_semana
    - 0.6 * es_festivo
    + 0.45 * llueve
    + 0.9 * evento_especial
)
demanda = demanda * peso_estacion
# En hora pico, los portales cargan más en la mañana y el centro en la tarde
demanda += 0.5 * pico_manana * (zona == "portal")
demanda += 0.5 * pico_tarde * (zona == "centro")
# Las líneas troncales B1/B2 concentran más pasajeros que las líneas auxiliares
demanda += 0.25 * np.isin(linea, ["B1", "B2"])

# Más buses ofertados reducen la saturación (efecto sobre ocupación)
ocupacion_pct = 35 + 30 * demanda - 0.9 * (buses_por_hora - 8)
ocupacion_pct += rng.normal(0, 7, N_REGISTROS)          # ruido
ocupacion_pct = np.clip(ocupacion_pct, 5, 130).round(1)

nivel = np.select(
    [ocupacion_pct < 55, ocupacion_pct < 85],
    ["bajo", "medio"],
    default="alto",
)

df = pd.DataFrame({
    "estacion": estacion,
    "linea": linea,
    "zona": zona,
    "hora": hora,
    "dia_semana": dia_semana,
    "es_fin_de_semana": es_fin_de_semana,
    "es_festivo": es_festivo,
    "llueve": llueve,
    "temperatura_c": temperatura,
    "evento_especial": evento_especial,
    "buses_por_hora": buses_por_hora,
    "ocupacion_pct": ocupacion_pct,
    "nivel_ocupacion": nivel,
})

# Introducimos algunos valores faltantes para practicar limpieza (≈1 %)
idx = rng.choice(N_REGISTROS, size=int(0.01 * N_REGISTROS), replace=False)
df.loc[idx, "temperatura_c"] = np.nan

salida = Path(__file__).parent / "datos" / "ocupacion_transporte.csv"
salida.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(salida, index=False, encoding="utf-8")

print(f"Dataset generado: {salida}  ({len(df)} filas)")
print(df["nivel_ocupacion"].value_counts(normalize=True).round(3))
