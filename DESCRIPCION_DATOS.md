# Descripción de los datos

Actividad 3 – Aprendizaje supervisado · Inteligencia Artificial · Corporación Universitaria Iberoamericana

## 1. Contexto del proyecto

En la Actividad 2 se modeló un sistema de transporte masivo tipo BRT (líneas **B1, B2, C1, D1 y E1**) con las estaciones Portal Norte, Calle 127, Usaquén, Calle 100, Calle 72, Calle 45, Centro, Av. Jiménez y Portal Sur. En esta actividad se agrega un componente de **aprendizaje supervisado** que predice el **nivel de ocupación** (`bajo`, `medio`, `alto`) de una estación según la hora, el día, el clima y la oferta de buses. Es un problema de **clasificación multiclase**.

Utilidad práctica: anticipar saturación para ajustar la frecuencia de buses y avisar a los usuarios, complementando la búsqueda de rutas de la Actividad 2.

## 2. Fuentes de datos reales identificadas

Para un modelo de producción se combinarían estas fuentes públicas. Los nombres exactos de los conjuntos deben confirmarse en cada portal antes de descargar, porque los catálogos cambian.

| Fuente | Qué aporta | Variables que alimenta |
|---|---|---|
| Portal Datos Abiertos Bogotá (datosabiertos.bogota.gov.co), que ya publica conjuntos de TransMilenio | Validaciones de entrada por estación y franja horaria; oferta de servicio | `estacion`, `hora`, `ocupacion_pct`, `buses_por_hora` |
| Datos Abiertos Colombia (datos.gov.co), series hidrometeorológicas del IDEAM | Precipitación y temperatura por estación meteorológica | `llueve`, `temperatura_c` |
| Calendario oficial de festivos de Colombia | Días festivos | `es_festivo` |
| Agendas de eventos de la ciudad (conciertos, partidos, marchas) | Eventos que concentran pasajeros | `evento_especial` |

**Por qué se usa una muestra sintética.** Los datos reales de validaciones no están publicados con el desglose por hora y línea que necesita el modelo, y el sistema de las actividades anteriores es un modelo académico simplificado. Como el enunciado lo permite, se desarrolló un dataset de muestra con la misma estructura que tendrían los datos reales.

> **Aviso importante:** el dataset es sintético. Las métricas del modelo demuestran que el flujo de trabajo funciona y que el árbol recupera los patrones que se programaron en el generador. **No** miden el desempeño que tendría con datos reales de operación.

## 3. Cómo se generó el dataset

Script: `generar_dataset.py` (semilla fija `42`, resultado reproducible).

1. Se eligen al azar estación, línea (una de las que realmente pasan por esa estación), hora (5 a 22), día de la semana, lluvia, festivo, evento y buses por hora.
2. Se calcula una demanda latente a partir de reglas inspiradas en la operación real: picos de 6–8 h y 17–19 h, menos pasajeros en fin de semana y festivos, más con lluvia o eventos, portales cargados en la mañana, centro cargado en la tarde y líneas troncales B1/B2 más usadas.
3. La demanda se convierte en `ocupacion_pct` restando el efecto de más buses y sumando **ruido aleatorio** (desviación 7 puntos), para que el problema no sea trivial.
4. `nivel_ocupacion` se obtiene al cortar `ocupacion_pct`: **bajo** < 55 %, **medio** 55–85 %, **alto** ≥ 85 %.
5. Se borra la temperatura en ~1 % de las filas para practicar el tratamiento de valores faltantes.

## 4. Diccionario de datos

Archivo: `datos/ocupacion_transporte.csv` · 5 000 filas · 13 columnas · codificación UTF-8.

| Columna | Tipo | Descripción | Valores / rango |
|---|---|---|---|
| `estacion` | texto | Estación observada | 9 estaciones del proyecto |
| `linea` | texto | Línea que atiende la estación en ese registro | B1, B2, C1, D1, E1 |
| `zona` | texto | Zona de la estación | portal, norte, centro |
| `hora` | entero | Hora del día | 5 a 22 |
| `dia_semana` | entero | Día de la semana | 0 = lunes … 6 = domingo |
| `es_fin_de_semana` | binario | Sábado o domingo | 0 / 1 |
| `es_festivo` | binario | Día festivo | 0 / 1 |
| `llueve` | binario | Hay lluvia | 0 / 1 |
| `temperatura_c` | decimal | Temperatura en °C | 8,0 a 27,7 (50 vacíos) |
| `evento_especial` | binario | Evento masivo cercano | 0 / 1 |
| `buses_por_hora` | entero | Buses ofertados por hora | 8 a 40 |
| `ocupacion_pct` | decimal | Ocupación de la estación (% de capacidad) | 5 a 130 |
| `nivel_ocupacion` | texto | **Variable objetivo** | bajo, medio, alto |

## 5. Análisis exploratorio

**Balance de clases** (casi equilibrado, no requiere remuestreo):

| Clase | Registros | Porcentaje | Ocupación media |
|---|---|---|---|
| alto | 1 721 | 34,4 % | 112,6 % |
| medio | 1 641 | 32,8 % | 69,8 % |
| bajo | 1 638 | 32,8 % | 35,5 % |

**Ocupación media por estación:** Av. Jiménez 87,2 % · Portal Sur 81,5 % · Centro 78,9 % · Portal Norte 77,6 % · Calle 72 77,1 % · Calle 45 74,9 % · Calle 100 71,2 % · Calle 127 61,3 % · Usaquén 50,6 %.

**Patrones visibles:**
- Entre las 6 y las 8 h, el 84 % de los registros es de ocupación alta y solo el 2 % baja.
- En fines de semana, el 62 % es de ocupación baja.

**Registros por línea:** B1 1 135 · B2 1 134 · C1 1 121 · D1 815 · E1 795 (D1 y E1 pasan por menos estaciones).

## 6. Preparación de los datos

- **Valores faltantes:** `temperatura_c` se imputa con la mediana (50 filas, 1 %).
- **Fuga de datos:** se **excluye `ocupacion_pct`** de las variables de entrada, porque la clase se calcula directamente a partir de ella y el modelo "haría trampa".
- **Variables categóricas:** `estacion`, `linea` y `zona` se codifican con *one-hot*.
- **Partición:** 75 % entrenamiento (3 750) y 25 % prueba (1 250), estratificada por clase y con semilla 42.

## 7. Limitaciones

- Datos sintéticos: las relaciones fueron programadas, no observadas.
- No hay dimensión temporal continua (fechas reales), por lo que no se evalúa la deriva del tiempo.
- Con datos reales habría que tratar además faltantes por fallas de torniquetes, estaciones cerradas y cambios de operación.
